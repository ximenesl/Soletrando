"""Módulo para gerenciar a conexão com o robô NAO."""
import qi
from config.settings import PORTA_NAO

class ConexaoNAO:
    """Gerencia a conexão com um robô NAO."""
    def __init__(self):
        self.ip = None
        self.porta = PORTA_NAO
        self.session = None
        self.app = None

    def conectar(self, ip: str) -> bool:
        """Conecta-se ao robô NAO em um determinado IP."""
        if self.session and self.session.isConnected():
            print(f"Já conectado ao NAO em {self.ip}:{self.porta}")
            return True
        try:
            self.ip = ip
            self.app = qi.Application(["Soletrando", f"--qi-url=tcp://{self.ip}:{self.porta}"])
            self.app.start()
            self.session = self.app.session
            if self.session.isConnected():
                print(f"Conectado ao NAO em {self.ip}:{self.porta}")
                return True
            return False
        except Exception as e:
            print(f"Erro ao conectar ao NAO: {e}")
            self.session = None
            self.app = None
            return False

    def desconectar(self):
        """Encerra a aplicação e a sessão com o NAO."""
        if self.app:
            print("Encerrando conexão com o NAO.")
            self.app.stop()
            self.app = None
            self.session = None

    def obter_servico(self, nome_servico: str):
        """Retorna um serviço da sessão do NAO se a conexão estiver ativa."""
        if self.session and self.session.isConnected():
            try:
                return self.session.service(nome_servico)
            except Exception as e:
                print(f"Erro ao obter o serviço '{nome_servico}': {e}")
        return None
