"""Módulo que define os comandos de interação com o robô NAO."""
import time
from services.conexao_nao import ConexaoNAO
from services.reconhecimento_voz import VOCABULARIO_LETRAS, MAPA_LETRAS_REVERSO
from thefuzz import process

class ComandosNAO:
    """Encapsula os comandos para o robô NAO."""
    def __init__(self, conexao: ConexaoNAO):
        self.conexao = conexao
        self.tts = self.conexao.obter_servico("ALTextToSpeech")
        self.asr = self.conexao.obter_servico("ALSpeechRecognition")
        self.memory = self.conexao.obter_servico("ALMemory")
        self.touch = self.conexao.obter_servico("ALTouch")
        self.leds = self.conexao.obter_servico("ALLeds")
        self.motion = self.conexao.obter_servico("ALMotion")
        self.audio_device = self.conexao.obter_servico("ALAudioDevice")

        self.assinantes_toque = {}
        self.escutando = False

        if self.tts:
            try:
                self.tts.setLanguage("Brazilian")
            except Exception as e:
                print(f"Erro ao configurar o idioma do NAO: {e}")
        
        if self.audio_device:
            try:
                # Seleciona os microfones frontais (melhor para reconhecimento de voz)
                # O 3 significa (1+2), que são os microfones da esquerda e direita.
                self.audio_device.setClientPreferences(self.__class__.__name__, 4, 3, 0)
            except Exception as e:
                print(f"Erro ao configurar os microfones do NAO: {e}")

        if self.asr:
            try:
                self.asr.setLanguage("Brazilian")
                # Ajustes para ambientes ruidosos
                self.asr.setParameter("EnergyThreshold", 3000) 
                self.asr.setParameter("Sensitivity", 0.4)
                self.asr.setVocabulary(VOCABULARIO_LETRAS, False)
            except Exception as e:
                print(f"Erro ao configurar o reconhecimento de voz do NAO: {e}")

    def dizer(self, texto: str):
        """Faz o robô NAO falar um texto."""
        if self.tts:
            try:
                self.tts.say(str(texto))
            except Exception as e:
                print(f"Erro ao tentar fazer o NAO falar: {e}")
        else:
            print(f"[SIMULAÇÃO] NAO diria: {texto}")

    def iniciar_escuta_soletracao(self, callback_letra: callable, callback_final: callable):
        """Inicia o reconhecimento de voz do NAO para soletrar uma palavra."""
        if not self.asr or not self.memory:
            self.dizer("Não consigo ouvir você agora.")
            callback_final()
            return

        self.escutando = True
        soletracao_atual = ""
        self.dizer("Pode começar a soletrar.")

        try:
            self.asr.subscribe("Soletrando_NAO")
            self.memory.insertData("WordRecognized", ["", 0]) # Limpa o dado anterior

            while self.escutando:
                time.sleep(0.5) # Pequena pausa para não sobrecarregar
                valor = self.memory.getData("WordRecognized")
                if not (valor and valor[0]):
                    continue

                palavra_ouvida = valor[0].lower()
                confianca = valor[1]
                self.memory.insertData("WordRecognized", ["", 0]) # Reseta para a próxima detecção

                if confianca < 0.35: # Limiar de confiança
                    continue

                letra = None
                if palavra_ouvida in MAPA_LETRAS_REVERSO:
                    letra = MAPA_LETRAS_REVERSO[palavra_ouvida]
                else:
                    # Usa fuzzy matching se a palavra exata não for encontrada
                    melhor_correspondecia, pontuacao = process.extractOne(palavra_ouvida, MAPA_LETRAS_REVERSO.keys())
                    if pontuacao >= 80:
                        letra = MAPA_LETRAS_REVERSO[melhor_correspondecia]
                        print(f"NAO Fuzzy match: ouviu '{palavra_ouvida}', entendeu como '{melhor_correspondecia}' (pontuação: {pontuacao})")

                if letra:
                    soletracao_atual += letra
                    callback_letra(soletracao_atual)

        except Exception as e:
            print(f"Ocorreu um erro durante o reconhecimento de voz do NAO: {e}")
            self.dizer("Desculpe, ocorreu um erro ao tentar ouvir.")
        finally:
            if self.asr:
                self.asr.unsubscribe("Soletrando_NAO")
            callback_final()
            print("NAO: Fim da escuta.")

    def parar_escuta(self):
        """Para o loop de reconhecimento de voz do NAO."""
        self.escutando = False

    def assinar_evento_toque(self, nome_evento: str, callback):
        """Inscreve-se em um evento de toque e mapeia para um callback."""
        if not self.memory or not self.touch:
            return

        if nome_evento in self.assinantes_toque:
            try:
                assinante, id_sinal = self.assinantes_toque[nome_evento]
                assinante.signal.disconnect(id_sinal)
            except Exception as e:
                print(f"Erro ao desconectar assinante existente: {e}")

        try:
            assinante = self.memory.subscriber(nome_evento)
            id_sinal = assinante.signal.connect(callback)
            self.assinantes_toque[nome_evento] = (assinante, id_sinal)
            print(f"Inscrito no evento de toque: {nome_evento}")
        except Exception as e:
            print(f"Erro ao se inscrever no evento de toque '{nome_evento}': {e}")

    def cancelar_assinaturas_toque(self):
        """Cancela todas as inscrições de eventos de toque."""
        for nome_evento, (assinante, id_sinal) in self.assinantes_toque.items():
            try:
                assinante.signal.disconnect(id_sinal)
                print(f"Inscrição do evento '{nome_evento}' cancelada.")
            except Exception as e:
                print(f"Erro ao cancelar a inscrição do evento '{nome_evento}': {e}")
        self.assinantes_toque = {}

    def piscar_olhos(self, cor: str, duracao: float = 1.0):
        """Pisca os LEDs dos olhos do NAO com uma cor específica."""
        if self.leds:
            try:
                self.leds.fadeRGB("FaceLeds", cor, 0.1)
                time.sleep(duracao)
                self.leds.fadeRGB("FaceLeds", "white", 0.1)
            except Exception as e:
                print(f"Erro ao piscar os olhos do NAO: {e}")

    def acenar(self):
        """Faz o NAO executar uma animação de aceno."""
        if self.motion:
            try:
                self.motion.wakeUp()
                self.motion.setStiffnesses("RArm", 1.0)
                names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
                angles = [0.5, -0.5, 0.0, 1.5]
                self.motion.setAngles(names, angles, 0.2)
                time.sleep(2)
                self.motion.setStiffnesses("RArm", 0.0)
            except Exception as e:
                print(f"Erro ao tentar fazer o NAO acenar: {e}")
