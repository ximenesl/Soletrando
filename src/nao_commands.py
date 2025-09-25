# Este arquivo define os comandos para interação com o robô NAO.

import time
import json
import os
import speech_recognition as sr
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
_LETTER_MAP_PATH = os.path.join(_SCRIPT_DIR, 'data', 'letter_map.json')

LETTER_MAP = load_letter_map_from_json(_LETTER_MAP_PATH)
REVERSE_LETTER_MAP = {spoken_word: letter for letter, spoken_words in LETTER_MAP.items() for spoken_word in spoken_words}
VOCABULARY = list(REVERSE_LETTER_MAP.keys())


class NaoCommands:
    def __init__(self, connection: NaoConnection):
        """Inicializa os serviços do NAO para fala e reconhecimento de voz."""
        self.connection = connection
        self.tts = connection.get_service("ALTextToSpeech")
        self.asr = connection.get_service("ALSpeechRecognition")
        self.memory = connection.get_service("ALMemory")
        self.touch = connection.get_service("ALTouch")
        self.left_hand_subscriber = None
        self.right_hand_subscriber = None
        self.is_listening = False

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

    def start_listening_for_spelling(self, on_letter_spelled, source='nao'):
        if source == 'nao':
            self._start_listening_from_nao(on_letter_spelled)
        elif source == 'pc':
            self._start_listening_from_pc(on_letter_spelled)

    def _start_listening_from_nao(self, on_letter_spelled):
        """Inicia o reconhecimento de voz para soletrar uma palavra."""
        if not self.asr or not self.memory or not LETTER_MAP:
            self.say("Não consigo ouvir você agora ou o mapa de letras falhou ao carregar.")
            return

        current_spelling = ""
        self.is_listening = True

        try:
            self.asr.setVocabulary(VOCABULARY, False)
            self.asr.subscribe("SpellingGame")
            self.say("Pode começar a soletrar.")

            self.memory.insertData("WordRecognized", ["", 0])

            while self.is_listening:
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

        except Exception as e:
            print(f"Ocorreu um erro durante o reconhecimento de voz: {e}")
            self.say("Desculpe, ocorreu um erro.")
        finally:
            if self.asr:
                self.asr.unsubscribe("SpellingGame")

    def stop_listening(self):
        """Para o loop de reconhecimento de voz."""
        self.is_listening = False

    def _start_listening_from_pc(self, on_letter_spelled):
        """Usa o microfone do PC para ouvir a palavra soletrada."""
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.say("Pode soletrar a palavra agora.")
            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=10)
                self.say("Ok, processando.")
                # Reconhece a fala usando Google Web Speech API
                spelled_word = r.recognize_google(audio, language='pt-BR')
                # Limpa a palavra para ter somente letras
                final_spelling = "".join(filter(str.isalpha, spelled_word)).lower()
                on_letter_spelled(final_spelling)
            except sr.UnknownValueError:
                self.say("Desculpe, não entendi o que você disse.")
                on_letter_spelled("") # Retorna vazio para indicar erro
            except sr.RequestError as e:
                self.say("Não foi possível se conectar ao serviço de reconhecimento de voz.")
                print(f"Erro no serviço Google Speech Recognition; {e}")
                on_letter_spelled("")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")
                on_letter_spelled("")

    def subscribe_to_touch_events(self, left_callback, right_callback):
        """Inscreve-se nos eventos de toque da mão e define os callbacks."""
        if not self.memory:
            return

        self.left_hand_callback = left_callback
        self.right_hand_callback = right_callback

        try:
            self.left_hand_subscriber = self.memory.subscriber("HandLeftBackTouched")
            self.left_hand_subscriber.signal.connect(self._on_left_hand_touched)
            
            self.right_hand_subscriber = self.memory.subscriber("HandRightBackTouched")
            self.right_hand_subscriber.signal.connect(self._on_right_hand_touched)
            print("Inscrito nos eventos de toque da mão.")
        except Exception as e:
            print(f"Erro ao se inscrever nos eventos de toque: {e}")

    def _on_left_hand_touched(self, value):
        """Callback para o toque na mão esquerda."""
        if value == 1.0 and self.left_hand_callback:
            print("Sensor da mão esquerda tocado.")
            self.left_hand_callback()

    def _on_right_hand_touched(self, value):
        """Callback para o toque na mão direita."""
        if value == 1.0 and self.right_hand_callback:
            print("Sensor da mão direita tocado.")
            self.right_hand_callback()

    def unsubscribe_touch_events(self):
        """Cancela a inscrição dos eventos de toque da mão."""
        try:
            if self.left_hand_subscriber:
                self.left_hand_subscriber.signal.disconnect()
            if self.right_hand_subscriber:
                self.right_hand_subscriber.signal.disconnect()
        except Exception as e:
            print(f"Erro ao cancelar a inscrição dos eventos de toque: {e}")

    def close(self):
        """Encerra a conexão com o robô."""
        self.unsubscribe_touch_events()
        self.connection.close()