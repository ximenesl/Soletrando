# Este arquivo define os comandos para interação com o robô NAO.

import time
import speech_recognition as sr
from nao_connection import NaoConnection

LETTER_MAP = {
    'a': 'a', 'á': 'a', 'ah': 'a',
    'bê': 'b', 'be': 'b', 'b': 'b',
    'cê': 'c', 'ce': 'c', 'c': 'c',
    'dê': 'd', 'de': 'd', 'd': 'd',
    'e': 'e', 'é': 'e', 'eh': 'e',
    'efe': 'f', 'éfe': 'f', 'f': 'f',
    'gê': 'g', 'ge': 'g', 'g': 'g',
    'agá': 'h', 'h': 'h',
    'i': 'i', 'í': 'i',
    'jota': 'j', 'j': 'j',
    'cá': 'k', 'ka': 'k', 'k': 'k',
    'ele': 'l', 'éle': 'l', 'l': 'l',
    'eme': 'm', 'éme': 'm', 'm': 'm', 'em': 'm',
    'ene': 'n', 'éne': 'n', 'n': 'n', 'en': 'n',
    'o': 'o', 'ó': 'o', 'oh': 'o',
    'pê': 'p', 'pe': 'p', 'p': 'p',
    'quê': 'q', 'que': 'q', 'q': 'q',
    'erre': 'r', 'érre': 'r', 'r': 'r',
    'esse': 's', 'ésse': 's', 's': 's', 'es': 's', 'és': 's',
    'tê': 't', 'te': 't', 't': 't',
    'u': 'u',
    'vê': 'v', 've': 'v', 'v': 'v',
    'dáblio': 'w', 'dablio': 'w', 'w': 'w',
    'xis': 'x', 'x': 'x', 'chis': 'x',
    'ípsilon': 'y', 'ipsilon': 'y', 'y': 'y',
    'zê': 'z', 'ze': 'z', 'z': 'z',
}

class NaoCommands:
    def __init__(self, connection: NaoConnection):
        self.connection = connection
        self.tts = connection.get_service("ALTextToSpeech")
        self.asr = connection.get_service("ALSpeechRecognition")
        self.memory = connection.get_service("ALMemory")
        self.touch = connection.get_service("ALTouch")
        self.left_hand_subscriber = None
        self.right_hand_subscriber = None

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

    def start_listening_for_spelling(self, on_letter_spelled, on_final_word, source='nao'):
        if source == 'nao':
            self._start_listening_from_nao(on_letter_spelled, on_final_word)
        elif source == 'pc':
            self._start_listening_from_pc(on_final_word)

    def _start_listening_from_nao(self, on_letter_spelled, on_final_word):
        """Inicia o reconhecimento de voz para soletrar uma palavra."""
        if not self.asr or not self.memory:
            self.say("Não consigo ouvir você agora.")
            return

        current_spelling = ""
        vocabulary = list(LETTER_MAP.keys()) + ["confirmar", "apagar"]
        
        try:
            self.asr.setVocabulary(vocabulary, False)
            self.asr.subscribe("SpellingGame")
            self.say("Pode começar a soletrar. Diga 'confirmar' quando terminar ou 'apagar' para a última letra.")
            
            self.memory.insertData("WordRecognized", ["", 0])

            while True:
                time.sleep(1)
                value = self.memory.getData("WordRecognized")
                if value and value[0]:
                    word = value[0].lower()
                    confidence = value[1]
                    self.memory.insertData("WordRecognized", ["", 0])

                    if confidence < 0.6:
                        continue

                    if word == "confirmar":
                        on_final_word(current_spelling)
                        break
                    elif word == "apagar":
                        if current_spelling:
                            current_spelling = current_spelling[:-1]
                            on_letter_spelled(current_spelling)
                    elif word in LETTER_MAP:
                        current_spelling += LETTER_MAP[word]
                        on_letter_spelled(current_spelling)
        except Exception as e:
            print(f"Ocorreu um erro durante o reconhecimento de voz: {e}")
            self.say("Desculpe, ocorreu um erro.")
        finally:
            if self.asr:
                self.asr.unsubscribe("SpellingGame")

    def _start_listening_from_pc(self, on_final_word):
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
                on_final_word(final_spelling)
            except sr.UnknownValueError:
                self.say("Desculpe, não entendi o que você disse.")
                on_final_word("") # Retorna vazio para indicar erro
            except sr.RequestError as e:
                self.say("Não foi possível se conectar ao serviço de reconhecimento de voz.")
                print(f"Erro no serviço Google Speech Recognition; {e}")
                on_final_word("")
            except Exception as e:
                print(f"Ocorreu um erro: {e}")
                on_final_word("")

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