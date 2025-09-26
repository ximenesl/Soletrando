"""Módulo do Controlador do Jogo, o cérebro da aplicação."""
import threading
from game.gerenciador_palavras import GerenciadorPalavras
from services.conexao_nao import ConexaoNAO
from services.comandos_nao import ComandosNAO
from services.reconhecimento_voz import ReconhecimentoVozPC

class ControladorJogo:
    """Orquestra a UI, a lógica do jogo e os serviços."""
    def __init__(self, app):
        self.app = app
        self.gerenciador_palavras = GerenciadorPalavras()
        self.reconhecimento_pc = ReconhecimentoVozPC()
        
        # --- Lógica do NAO ---
        self.conexao_nao = ConexaoNAO()
        self.comandos_nao: ComandosNAO | None = None

        # --- Estado do Jogo ---
        self.palavra_atual = ""
        self.soletracao_usuario = ""
        self.nivel_atual = "1"
        self.fonte_microfone = "pc" # Padrão para o microfone do PC
        self.escutando = False
        self.thread_escuta = None

    def iniciar_jogo(self):
        """Carrega as palavras do nível selecionado e inicia a primeira rodada."""
        if self.gerenciador_palavras.carregar_palavras(self.nivel_atual):
            self.iniciar_nova_rodada()
        else:
            self.app.mostrar_erro(f"Não foi possível carregar palavras para o nível {self.nivel_atual}.")

    def iniciar_nova_rodada(self):
        """Pede uma nova palavra e atualiza a UI."""
        self.parar_escuta_voz() # Garante que a escuta anterior pare
        self.soletracao_usuario = ""
        nova_palavra = self.gerenciador_palavras.obter_nova_palavra()

        if not nova_palavra:
            self.app.mostrar_erro("Todas as palavras do nível foram concluídas!")
            if self.comandos_nao: self.comandos_nao.dizer("Você completou todas as palavras!")
            return

        self.palavra_atual = nova_palavra
        
        self.app.mudar_para_tela("soletrar")
        self.app.tela_soletrar.atualizar_exibicao_palavra(self.palavra_atual)
        
        if self.comandos_nao:
            self.comandos_nao.dizer(f"A nova palavra é: {self.palavra_atual}")

    def iniciar_soletracao(self):
        """Inicia o reconhecimento de voz em uma thread separada."""
        if self.escutando:
            print("Já estou escutando.")
            return

        self.escutando = True
        self.soletracao_usuario = ""
        self.app.tela_soletrar.limpar_letras_soletradas()
        self.app.tela_soletrar.definir_status(f"Ouvindo pelo {self.fonte_microfone.upper()}...", "white")
        self.app.tela_soletrar.configurar_estado_botoes("disabled")

        if self.fonte_microfone == 'pc':
            self.thread_escuta = threading.Thread(target=self.reconhecimento_pc.ouvir_soletracao,
                                                  args=(self.atualizar_soletracao_da_thread, self.finalizar_escuta_da_thread),
                                                  daemon=True)
        elif self.fonte_microfone == 'nao' and self.comandos_nao:
            self.thread_escuta = threading.Thread(target=self.comandos_nao.iniciar_escuta_soletracao,
                                                  args=(self.atualizar_soletracao_da_thread, self.finalizar_escuta_da_thread),
                                                  daemon=True)
        
        if self.thread_escuta:
            self.thread_escuta.start()

    def parar_escuta_voz(self):
        """Sinaliza para a thread de escuta parar."""
        if self.escutando:
            print("Parando a escuta...")
            self.escutando = False
            if self.fonte_microfone == 'pc':
                self.reconhecimento_pc.parar_de_ouvir()
            elif self.fonte_microfone == 'nao' and self.comandos_nao:
                self.comandos_nao.parar_escuta()
            
            if self.thread_escuta and self.thread_escuta.is_alive():
                self.thread_escuta.join(timeout=1) # Espera um pouco pela thread
            
            self.finalizar_escuta_da_thread()

    def atualizar_soletracao_da_thread(self, soletracao: str):
        """Callback da thread de reconhecimento para atualizar a UI."""
        self.soletracao_usuario = soletracao
        self.app.after(0, self.app.tela_soletrar.atualizar_letras_soletradas, self.soletracao_usuario)

    def finalizar_escuta_da_thread(self):
        """Callback para quando a thread de escuta termina."""
        self.escutando = False
        self.app.after(0, self.app.tela_soletrar.definir_status, "")
        self.app.after(0, self.app.tela_soletrar.configurar_estado_botoes, "normal")

    def finalizar_verificacao(self):
        """Para a escuta e verifica se a soletração está correta."""
        self.parar_escuta_voz()

        soletracao_normalizada = self.soletracao_usuario.lower().replace(" ", "")
        palavra_normalizada = self.palavra_atual.lower()
        acertou = soletracao_normalizada == palavra_normalizada

        if acertou:
            resultado_texto = "Parabéns, você acertou!"
            if self.comandos_nao: self.comandos_nao.piscar_olhos("green")
        else:
            resultado_texto = f"Você errou! A palavra era '{self.palavra_atual.upper()}'"
            if self.comandos_nao: self.comandos_nao.piscar_olhos("red")
        
        if self.comandos_nao: self.comandos_nao.dizer(resultado_texto)
        
        self.app.mudar_para_tela("resultado")
        self.app.tela_resultado.definir_resultado(self.palavra_atual, self.soletracao_usuario, acertou)

    # --- Métodos de Delegação (Callbacks da UI) ---
    def definir_nivel(self, nivel: str):
        self.nivel_atual = nivel
        self.iniciar_jogo()

    def definir_fonte_microfone(self, fonte: str):
        if fonte.lower() == 'nao' and not self.comandos_nao:
            self.app.mostrar_erro("Conecte-se ao NAO para usar seu microfone.")
            self.app.definir_selecao_mic('pc') # Volta para o PC
            return
        self.fonte_microfone = fonte.lower()
        print(f"Fonte de áudio alterada para: {self.fonte_microfone}")

    # --- Métodos de Conexão NAO ---
    def conectar_nao(self, ip: str):
        if self.conexao_nao.conectar(ip):
            self.comandos_nao = ComandosNAO(self.conexao_nao)
            self.app.painel_nao.atualizar_status(conectado=True, ip=ip)
            self.comandos_nao.dizer("Olá! Estou pronto para soletrar.")
            self._assinar_eventos_nao()
        else:
            self.app.painel_nao.atualizar_status(conectado=False)
            self.app.mostrar_erro(f"Falha ao conectar no IP {ip}")

    def _assinar_eventos_nao(self):
        if not self.comandos_nao:
            return
        self.comandos_nao.assinar_evento_toque("HandLeftBackTouched", self._callback_mao_esquerda)
        self.comandos_nao.assinar_evento_toque("HandRightBackTouched", self._callback_mao_direita)

    def _callback_mao_esquerda(self, value):
        if value == 1.0:
            print("Toque na mão esquerda detectado.")
            if self.escutando:
                self.parar_escuta_voz()
            self.soletracao_usuario = ""
            self.app.after(0, self.app.tela_soletrar.limpar_letras_soletradas)
            if self.comandos_nao:
                self.comandos_nao.dizer("Apagado")

    def _callback_mao_direita(self, value):
        if value == 1.0:
            print("Toque na mão direita detectado.")
            if self.comandos_nao:
                self.comandos_nao.dizer("Confirmado")
            self.app.after(0, self.finalizar_verificacao)

    def desconectar_nao(self):
        if self.comandos_nao:
            self.comandos_nao.dizer("Até mais!")
            self.comandos_nao.cancelar_assinaturas_toque()
        self.conexao_nao.desconectar()
        self.comandos_nao = None
        self.app.painel_nao.atualizar_status(conectado=False)
        if self.fonte_microfone == 'nao': # Se estava usando o mic do NAO, volta pro PC
            self.definir_fonte_microfone('pc')
            self.app.definir_selecao_mic('pc')

    def fechar_aplicacao(self):
        """Limpa os recursos antes de fechar."""
        self.parar_escuta_voz()
        self.desconectar_nao()
        self.app.destroy()
