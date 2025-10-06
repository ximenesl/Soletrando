"""Módulo que define os comandos de interação com o robô NAO."""
import time
from services.conexao_nao import ConexaoNAO

class ComandosNAO:
    """Encapsula os comandos para o robô NAO."""
    def __init__(self, conexao: ConexaoNAO):
        self.conexao = conexao
        self.tts = self.conexao.obter_servico("ALTextToSpeech")
        self.motion = self.conexao.obter_servico("ALMotion")
        self.leds = self.conexao.obter_servico("ALLeds")
        self.memory = self.conexao.obter_servico("ALMemory")
        self.animation_player = self.conexao.obter_servico("ALAnimationPlayer")
        self.eventos_toque = {}

        if self.tts:
            self._configurar_idioma()

    def _configurar_idioma(self, idioma="Brazilian"):
        try:
            self.tts.setLanguage(idioma)
        except Exception as e:
            print(f"Erro ao configurar o idioma do NAO: {e}")

    def dizer(self, texto: str):
        """Faz o robô NAO falar um texto."""
        if self.tts:
            try:
                self.tts.say(texto)
            except Exception as e:
                print(f"Erro ao tentar fazer o NAO falar: {e}")
        else:
            print(f"[SIMULAÇÃO] NAO diria: {texto}")

    def assinar_evento_toque(self, evento: str, callback: callable):
        """Assina um evento de toque e o associa a um callback."""
        if not self.memory:
            return
        try:
            assinatura = self.memory.subscriber(evento)
            id_conexao = assinatura.signal.connect(callback)
            self.eventos_toque[evento] = (assinatura, id_conexao)
            print(f"Assinatura para o evento '{evento}' criada com sucesso.")
        except Exception as e:
            print(f"Erro ao assinar o evento '{evento}': {e}")

    def cancelar_assinaturas_toque(self):
        """Cancela todas as assinaturas de eventos de toque."""
        for evento, (assinatura, id_conexao) in self.eventos_toque.items():
            try:
                assinatura.signal.disconnect(id_conexao)
                print(f"Assinatura para o evento '{evento}' cancelada.")
            except Exception as e:
                print(f"Erro ao cancelar a assinatura do evento '{evento}': {e}")
        self.eventos_toque.clear()

    def piscar_olhos(self, cor: str, duracao=0.5):
        """Pisca os LEDs dos olhos do NAO com uma cor específica."""
        if self.leds:
            try:
                self.leds.fadeRGB("FaceLeds", cor, duracao)
                time.sleep(duracao)
                self.leds.fadeRGB("FaceLeds", "black", duracao)
            except Exception as e:
                print(f"Erro ao piscar os olhos do NAO: {e}")

    def acenar(self):
        """Faz o NAO executar uma animação de aceno."""
        if not self.animation_player or not self.motion:
            print("Serviços de animação ou movimento não disponíveis.")
            return
        try:
            # Garante que o robô esteja em uma postura segura
            if not self.motion.robotIsWakeUp():
                self.motion.wakeUp()
            
            # Caminho da animação de aceno
            nome_animacao = "Gestures/Hey_1"
            
            # Executa a animação
            future = self.animation_player.run(nome_animacao, _async=True)
            future.value() # Espera a animação terminar

        except Exception as e:
            print(f"Erro ao tentar fazer o NAO acenar: {e}")
