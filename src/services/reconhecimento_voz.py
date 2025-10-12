"""Módulo para reconhecimento de voz."""
import speech_recognition as sr
import json
import sys
from thefuzz import process
from config.settings import ARQUIVO_MAPA_LETRAS

def carregar_mapa_letras(caminho_arquivo: str) -> tuple[dict, dict, list]:
    """Carrega o mapa de letras de um arquivo JSON."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            mapa_letras = json.load(f)
        
        mapa_reverso = {palavra_falada: letra 
                        for letra, palavras_faladas in mapa_letras.items() 
                        for palavra_falada in palavras_faladas}
        
        vocabulario = list(mapa_reverso.keys())

        return mapa_letras, mapa_reverso, vocabulario
    except (FileNotFoundError, json.JSONDecodeError):
        return {}, {}, []

MAPA_LETRAS, MAPA_LETRAS_REVERSO, VOCABULARIO_LETRAS = carregar_mapa_letras(ARQUIVO_MAPA_LETRAS)

class ReconhecimentoVozPC:
    """Gerencia o reconhecimento de voz usando o microfone do PC."""
    def __init__(self, device_index: int | None = None):
        self.reconhecedor = sr.Recognizer()
        self.reconhecedor.pause_threshold = 1.5
        self.escutando = False
        self.device_index = device_index

    def ouvir_soletracao(self, soletracao_inicial: str, callback_letra: callable, callback_final: callable):
        """Inicia o reconhecimento contínuo de letras a partir de um estado inicial."""
        self.escutando = True
        soletracao_atual = soletracao_inicial

        try:
            with sr.Microphone(device_index=self.device_index) as source:
                self.reconhecedor.adjust_for_ambient_noise(source, duration=0.5)

                while self.escutando:
                    try:
                        audio = self.reconhecedor.listen(source, timeout=2, phrase_time_limit=2)
                        texto = self.reconhecedor.recognize_google(audio, language='pt-BR').lower()

                        melhor_correspondecia, pontuacao = process.extractOne(texto, VOCABULARIO_LETRAS)
                        
                        if pontuacao >= 75:
                            letra = MAPA_LETRAS_REVERSO[melhor_correspondecia]
                            soletracao_atual += letra
                            callback_letra(soletracao_atual) 

                    except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
                        continue
        except Exception:
            pass
        finally:
            self.escutando = False
            callback_final()

    def parar_de_ouvir(self):
        """Para o loop de reconhecimento de voz."""
        self.escutando = False