"""Módulo para gerenciar as palavras do jogo."""
import os
import random
from config.settings import CAMINHO_LISTAS_PALAVRAS

class GerenciadorPalavras:
    """Carrega e gerencia as listas de palavras para cada nível."""
    def __init__(self):
        self.palavras_do_nivel = []
        self.palavras_disponiveis = []

    def carregar_palavras(self, nivel: str):
        """Carrega a lista de palavras para um nível específico."""
        caminho_arquivo = os.path.join(CAMINHO_LISTAS_PALAVRAS, f"{nivel}_ano.txt")
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                self.palavras_do_nivel = [linha.strip().lower() for linha in f if linha.strip()]
                self.reiniciar_rodada()
                return True
        except FileNotFoundError:
            print(f"Arquivo de palavras não encontrado: {caminho_arquivo}")
            self.palavras_do_nivel = []
            self.palavras_disponiveis = []
            return False

    def obter_nova_palavra(self) -> str | None:
        """Retorna uma nova palavra aleatória e a remove da lista de disponíveis."""
        if not self.palavras_disponiveis:
            # Se acabaram as palavras, reembaralha a lista original
            self.reiniciar_rodada()
            if not self.palavras_disponiveis: # Ainda vazia? Então não há palavras.
                return None
        
        return self.palavras_disponiveis.pop()

    def reiniciar_rodada(self):
        """Reembaralha as palavras do nível atual."""
        self.palavras_disponiveis = self.palavras_do_nivel.copy()
        random.shuffle(self.palavras_disponiveis)
