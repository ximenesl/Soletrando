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
