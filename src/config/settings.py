"""Módulo de Configurações."""
import os

# Diretório base do script (src)
DIRETORIO_SCRIPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurações do NAO
PORTA_NAO = 9559

# Caminhos
CAMINHO_ASSETS = os.path.join(DIRETORIO_SCRIPT, "assets")
CAMINHO_IMAGENS = os.path.join(CAMINHO_ASSETS, "img")
CAMINHO_LISTAS_PALAVRAS = os.path.join(DIRETORIO_SCRIPT, "word_lists")
CAMINHO_DADOS = os.path.join(DIRETORIO_SCRIPT, "data")

# Arquivos
ARQUIVO_LOGO = os.path.join(CAMINHO_IMAGENS, "SOLETRANDO.png")
ARQUIVO_MAPA_LETRAS = os.path.join(CAMINHO_DADOS, "letter_map.json")
