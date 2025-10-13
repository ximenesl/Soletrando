



"""Módulo do Gerenciador do Jogo, o cérebro do back-end."""

import threading

from naoqi import ALBroker

from game.gerenciador_palavras import GerenciadorPalavras

from services.conexao_nao import ConexaoNAO, ReconhecimentoVozNAO, NOME_MODULO_AUDIO

from services.comandos_nao import ComandosNAO

from services.reconhecimento_voz import ReconhecimentoVozPC
from services.processador_audio import ProcessadorAudioMultiCanal



class GerenciadorJogo:

    """Orquestra a lógica do jogo e os serviços."""

    def __init__(self):

        self.gerenciador_palavras = GerenciadorPalavras()

        self.reconhecimento_pc: ReconhecimentoVozPC | None = None
        self.processador_audio: ProcessadorAudioMultiCanal | None = None

        

        # --- Lógica do NAO ---

        self.conexao_nao = ConexaoNAO()

        self.comandos_nao: ComandosNAO | None = None

        self.reconhecimento_nao: ReconhecimentoVozNAO | None = None

        self.broker_nao: ALBroker | None = None



        # --- Estado do Jogo ---

        self.palavra_atual = ""

        self.soletracao_usuario = ""

        self.nivel_atual = "1"

        self.fonte_microfone = "pc" 

        self.escutando = False

        self.thread_escuta = None # Não é mais usado para NAO ou Hibrido

        self.jogo_iniciado = False

        self.erro = None



    def iniciar_jogo(self):

        """Carrega as palavras do nível selecionado e inicia a primeira rodada."""

        if self.gerenciador_palavras.carregar_palavras(self.nivel_atual):

            self.jogo_iniciado = True

            return self.iniciar_nova_rodada()

        else:

            self.erro = f"Não foi possível carregar palavras para o nível {self.nivel_atual}."

            return {"erro": self.erro}



    def iniciar_nova_rodada(self):

        """Pede uma nova palavra e atualiza o estado."""

        self.parar_escuta_voz()

        self.soletracao_usuario = ""

        nova_palavra = self.gerenciador_palavras.obter_nova_palavra()



        if not nova_palavra:

            self.erro = "Todas as palavras do nível foram concluídas!"

            if self.comandos_nao: self.comandos_nao.dizer("Você completou todas as palavras!")

            return {"status": "fim_de_jogo", "mensagem": self.erro}



        self.palavra_atual = nova_palavra

        

        if self.comandos_nao:

            self.comandos_nao.dizer(f"A nova palavra é: {self.palavra_atual}")

        

        return {"palavra": self.palavra_atual}



        def iniciar_soletracao(self, device: int | str | None = None):



            """Inicia o reconhecimento de voz em uma thread separada."""



    



            if self.escutando:



    



                return {"status": "ocupado", "mensagem": "Já estou escutando."}



    



            self.escutando = True



            



            try:



                if self.fonte_microfone == 'pc':



                    self.reconhecimento_pc = ReconhecimentoVozPC(device_index=device)



                    self.thread_escuta = threading.Thread(



                        target=self.reconhecimento_pc.ouvir_soletracao,



                        args=(self.soletracao_usuario, self._atualizar_soletracao, self._finalizar_escuta),



                        daemon=True



                    )



                    self.thread_escuta.start()



    



                elif self.fonte_microfone == 'nao' and self.reconhecimento_nao:



                    if self.comandos_nao: self.comandos_nao.dizer("Pode começar a soletrar.")



                    self.reconhecimento_nao.iniciar_escuta(self.soletracao_usuario)



    



                elif self.fonte_microfone == 'hibrido' and self.reconhecimento_nao:



                    if self.comandos_nao: self.comandos_nao.dizer("Modo de cancelamento de ruído ativado.")



                    self.processador_audio = ProcessadorAudioMultiCanal(



                        reconhecimento_nao=self.reconhecimento_nao,



                        soletracao_inicial=self.soletracao_usuario,



                        callback_letra=self._atualizar_soletracao,



                        callback_final=self._finalizar_escuta,



                        device_index=device



                    )



                    self.processador_audio.iniciar()



                else:
                self.escutando = False
                return {"status": "erro", "mensagem": f"Fonte de microfone '{self.fonte_microfone}' não está pronta."}

            return {"status": "sucesso", "mensagem": f"Ouvindo pelo {self.fonte_microfone.upper()}..."}
        except Exception as e:
            self.escutando = False
            return {"status": "erro", "mensagem": f"Falha ao iniciar escuta: {e}"}


    def parar_escuta_voz(self):

        """Sinaliza para a thread de escuta parar."""

        if not self.escutando:
            return {"status": "parado"}

        if self.fonte_microfone == 'pc' and self.reconhecimento_pc:
            self.reconhecimento_pc.parar_de_ouvir()
            if self.thread_escuta and self.thread_escuta.is_alive():
                self.thread_escuta.join(timeout=1)

        elif self.fonte_microfone == 'nao' and self.reconhecimento_nao:
            self.reconhecimento_nao.parar_escuta()

        elif self.fonte_microfone == 'hibrido' and self.processador_audio:
            self.processador_audio.parar()
            self.processador_audio = None

        self._finalizar_escuta()
        return {"status": "parado"}



    def _atualizar_soletracao(self, soletracao: str):

        """Callback para atualizar a soletração."""

        self.soletracao_usuario = soletracao



    def _finalizar_escuta(self):

        """Callback para quando a escuta termina."""

        self.escutando = False



    def verificar_soletracao(self):

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

        

        return {

            "resultado": "acertou" if acertou else "errou",

            "palavra_correta": self.palavra_atual,

            "sua_soletracao": self.soletracao_usuario

        }



    def apagar_ultima_letra(self):

        """Apaga a última letra da soletração."""

        self.parar_escuta_voz()

        if self.soletracao_usuario:

            self.soletracao_usuario = self.soletracao_usuario[:-1]

        return {"soletracao_atual": self.soletracao_usuario}

   

    def definir_nivel(self, nivel: str):

        self.nivel_atual = nivel

        if self.jogo_iniciado:

            return self.iniciar_jogo()

        return {"status": "nível definido"}



    def definir_fonte_microfone(self, fonte: str):
        fonte_lower = fonte.lower()
        if fonte_lower in ('nao', 'hibrido') and not self.comandos_nao:
            return {"status": "erro", "mensagem": "Conecte-se ao NAO para usar este microfone."}
        self.fonte_microfone = fonte_lower
        return {"status": "fonte de microfone definida", "fonte": self.fonte_microfone}

    

    def conectar_nao(self, ip: str, port: int = 9559):

        """Conecta ao NAO, inicializa o broker e o módulo de reconhecimento remoto."""

        try:
            # O broker é necessário para o ReconhecimentoVozNAO e ProcessadorAudioMultiCanal
            self.broker_nao = ALBroker("pythonBroker", "0.0.0.0", 0, ip, port)

            # O ReconhecimentoVozNAO agora é apenas um transportador de áudio
            self.reconhecimento_nao = ReconhecimentoVozNAO(
                NOME_MODULO_AUDIO, 
                self._atualizar_soletracao, # Callback de letra (usado no modo 'nao')
                self._finalizar_escuta # Callback final
            )

        except Exception as e:
            return {"status": "erro", "mensagem": f"Falha ao iniciar broker do NAO: {e}"}



        if self.conexao_nao.conectar(ip, port):

            self.comandos_nao = ComandosNAO(self.conexao_nao)

            self.comandos_nao.dizer("Olá! Estou pronto para soletrar.")

            return {"status": "conectado", "ip": ip}

        else:

            self.desconectar_nao()

            return {"status": "erro", "mensagem": f"Falha ao conectar no IP {ip}"}



    def desconectar_nao(self):

        """Desconecta do NAO e finaliza o broker e módulos."""

        self.parar_escuta_voz()

        if self.comandos_nao:

            self.comandos_nao.dizer("Até mais!")

        

        self.conexao_nao.desconectar()

        self.comandos_nao = None
        self.reconhecimento_nao = None # Limpa a instância


        if self.broker_nao:

            self.broker_nao.shutdown()

            self.broker_nao = None



        if self.fonte_microfone in ('nao', 'hibrido'): 

            self.definir_fonte_microfone('pc')

        return {"status": "desconectado"}



    def obter_estado(self):

        return {

            "palavra_atual": self.palavra_atual,

            "soletracao_usuario": self.soletracao_usuario,

            "nivel_atual": self.nivel_atual,

            "fonte_microfone": self.fonte_microfone,

            "escutando": self.escutando,

            "jogo_iniciado": self.jogo_iniciado,

            "erro": self.erro,

            "nao_conectado": self.comandos_nao is not None

        }


