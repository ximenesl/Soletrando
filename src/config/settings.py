"""Módulo de Configurações."""
import os

# Diretório base do script (src)
DIRETORIO_SCRIPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurações do NAO
PORTA_NAO = 9559

# Caminhos
CAMINHO_LISTAS_PALAVRAS = os.path.join(DIRETORIO_SCRIPT, "word_lists")
CAMINHO_DADOS = os.path.join(DIRETORIO_SCRIPT, "data")

# Arquivos
ARQUIVO_MAPA_LETRAS = os.path.join(CAMINHO_DADOS, "letter_map.json")
