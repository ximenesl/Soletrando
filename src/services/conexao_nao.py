"""Módulo para gerenciar a conexão com o robô NAO."""
import qi
from config.settings import PORTA_NAO

class ConexaoNAO:
    """Gerencia a conexão com um robô NAO."""
    def __init__(self):
        self.ip = None
        self.porta = PORTA_NAO
        self.app = None
        self.sessao = None

    def conectar(self, ip: str):
        """Conecta-se ao robô NAO em um determinado IP."""
        if self.sessao and self.ip == ip:
            print(f"Já conectado ao NAO em {self.ip}:{self.porta}")
            return True
        
        self.desconectar() # Garante que qualquer conexão anterior seja fechada
        self.ip = ip

        try:
            url_conexao = f"tcp://{self.ip}:{self.porta}"
            self.app = qi.Application(["Soletrando", f"--qi-url={url_conexao}"])
            self.app.start()
            self.sessao = self.app.session
            print(f"Conectado ao NAO em {self.ip}:{self.porta}")
            return True
        except RuntimeError as e:
            print(f"Erro ao conectar ao NAO: {e}")
            self.app = None
            self.sessao = None
            return False

    def desconectar(self):
        """Encerra a aplicação e a sessão com o NAO."""
        if self.app:
            print("Encerrando conexão com o NAO.")
            self.app.stop()
            self.app = None
            self.sessao = None
            self.ip = None

    def obter_servico(self, nome_servico: str):
        """Retorna um serviço da sessão do NAO se a conexão estiver ativa."""
        if self.sessao:
            try:
                return self.sessao.service(nome_servico)
            except Exception as e:
                print(f"Erro ao obter o serviço '{nome_servico}': {e}")
        return None
