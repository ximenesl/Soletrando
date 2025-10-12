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
            self.leds = self.conexao.obter_servico("ALLeds")
            self.motion = self.conexao.obter_servico("ALMotion")
            self.audio_device = self.conexao.obter_servico("ALAudioDevice")
    
            self.escutando = False
    
            if self.tts:
                try:
                    self.tts.setLanguage("Brazilian")
                except Exception:
                    pass
            
            if self.audio_device:
                try:
                    # Seleciona os microfones frontais (melhor para reconhecimento de voz)
                    # O 3 significa (1+2), que são os microfones da esquerda e direita.
                    self.audio_device.setClientPreferences(self.__class__.__name__, 4, 3, 0)
                except Exception:
                    pass
    
            if self.asr:
                try:
                    self.asr.setLanguage("Brazilian")
                    # Ajustes para ambientes ruidosos
                    self.asr.setParameter("EnergyThreshold", 3000) 
                    self.asr.setParameter("Sensitivity", 0.6)
                    self.asr.setVocabulary(VOCABULARIO_LETRAS, False)
                except Exception:
                    pass
    
    def dizer(self, texto: str):
            """Faz o robô NAO falar um texto."""
            if self.tts:
                try:
                    self.tts.say(str(texto))
                except Exception:
                    pass
    
    def iniciar_escuta_soletracao(self, soletracao_inicial: str, callback_letra: callable, callback_final: callable):
            """Inicia o reconhecimento de voz do NAO para soletrar uma palavra."""
            if not self.asr or not self.memory:
                self.dizer("Não consigo ouvir você agora.")
                callback_final()
                return
    
            self.escutando = True
            soletracao_atual = soletracao_inicial
            self.dizer("Pode começar a soletrar.")
    
            try:
                self.asr.subscribe("Soletrando_NAO")
                self.memory.insertData("WordRecognized", ["", 0])
    
                while self.escutando:
                    time.sleep(0.5)
                    valor = self.memory.getData("WordRecognized")
                    if not (valor and valor[0]):
                        continue
    
                    palavra_ouvida = valor[0].lower()
                    confianca = valor[1]
                    self.memory.insertData("WordRecognized", ["", 0]) 
    
                    if confianca < 0.35: 
                        continue
    
                    letra = None
                    if palavra_ouvida in MAPA_LETRAS_REVERSO:
                        letra = MAPA_LETRAS_REVERSO[palavra_ouvida]
                    else:
                       
                        melhor_correspondecia, pontuacao = process.extractOne(palavra_ouvida, MAPA_LETRAS_REVERSO.keys())
                        if pontuacao >= 80:
                            letra = MAPA_LETRAS_REVERSO[melhor_correspondecia]
    
                    if letra:
                        soletracao_atual += letra
                        callback_letra(soletracao_atual)
    
            except Exception:
                self.dizer("Desculpe, ocorreu um erro ao tentar ouvir.")
            finally:
                if self.asr:
                    self.asr.unsubscribe("Soletrando_NAO")
                callback_final()

    def parar_escuta(self):
        """Para o loop de reconhecimento de voz do NAO."""
        self.escutando = False



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
