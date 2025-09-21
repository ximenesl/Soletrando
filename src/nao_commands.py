# Este arquivo define os comandos para interação com o robô NAO.

import time
import json
import os
from nao_connection import NaoConnection
from thefuzz import process

def load_letter_map_from_json(file_path: str) -> dict:
    """Carrega o mapa de letras de um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo de mapa de letras '{file_path}' não foi encontrado.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{file_path}' não é um JSON válido.")
        return {}

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
_LETTER_MAP_PATH = os.path.join(_PROJECT_ROOT, 'data', 'letter_map.json')

LETTER_MAP = load_letter_map_from_json(_LETTER_MAP_PATH)
REVERSE_LETTER_MAP = {spoken_word: letter for letter, spoken_words in LETTER_MAP.items() for spoken_word in spoken_words}
VOCABULARY = list(REVERSE_LETTER_MAP.keys()) + ["confirmar", "apagar"]


class NaoCommands:
    def __init__(self, connection: NaoConnection):
        """Inicializa os serviços do NAO para fala e reconhecimento de voz."""
        self.connection = connection
        self.tts = connection.get_service("ALTextToSpeech")
        self.asr = connection.get_service("ALSpeechRecognition")
        self.memory = connection.get_service("ALMemory")
        if self.asr:
            try:
                self.asr.setLanguage("Brazilian")
                self.asr.setParameter("Sensitivity", 0.7)
                self.asr.setParameter("NoiseSuppression", True)
            except Exception as e:
                print(f"Erro ao configurar o idioma: {e}")

    def say(self, text):
        """Faz o robô NAO falar um texto."""
        if self.tts:
            try:
                self.tts.setLanguage("Brazilian")
                self.tts.say(str(text))
            except Exception as e:
                print(f"Erro ao tentar fazer o NAO falar: {e}")
        else:
            print(f"[SIMULAÇÃO] NAO diria: {text}")

    def start_listening_for_spelling(self, on_letter_spelled, on_final_word):
        """Inicia o reconhecimento de voz para soletrar uma palavra."""
        if not self.asr or not self.memory or not LETTER_MAP:
            self.say("Não consigo ouvir você agora ou o mapa de letras falhou ao carregar.")
            return

        current_spelling = ""
        
        try:
            self.asr.setVocabulary(VOCABULARY, False)
            self.asr.subscribe("SpellingGame")
            self.say("Pode começar a soletrar. Diga 'confirmar' quando terminar ou 'apagar' para a última letra.")
            
            self.memory.insertData("WordRecognized", ["", 0])

            while True:
                time.sleep(1)
                value = self.memory.getData("WordRecognized")
                if not (value and value[0]):
                    continue

                word = value[0].lower()
                confidence = value[1]
                self.memory.insertData("WordRecognized", ["", 0])

                if confidence < 0.4:
                    continue

                letter = None
                if word in REVERSE_LETTER_MAP:
                    letter = REVERSE_LETTER_MAP[word]
                else:
                    best_match, score = process.extractOne(word, REVERSE_LETTER_MAP.keys())
                    if score >= 80:
                        letter = REVERSE_LETTER_MAP[best_match]
                        print(f"Fuzzy match: ouvi '{word}', entendi como '{best_match}' (score: {score})")

                if letter:
                    current_spelling += letter
                    on_letter_spelled(current_spelling)
                elif word == "confirmar":
                    on_final_word(current_spelling)
                    break
                elif word == "apagar":
                    if current_spelling:
                        current_spelling = current_spelling[:-1]
                        on_letter_spelled(current_spelling)
                            
        except Exception as e:
            print(f"Ocorreu um erro durante o reconhecimento de voz: {e}")
            self.say("Desculpe, ocorreu um erro.")
        finally:
            self.asr.unsubscribe("SpellingGame")

    def close(self):
        """Encerra a conexão com o robô."""
        self.connection.close()