import customtkinter as ctk
from PIL import Image
import random
import threading
import os
from nao_connection import NaoConnection
from nao_commands import NaoCommands
from emoji_map import EMOJI_MAP

NAO_PORT = 9559

class SoletrandoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SOLETRANDO COM NAO")
        self.geometry("700x650")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0077CC")

        self.nao_commands: NaoCommands | None = None
        self.current_word = ""
        self.user_spelling = ""
        
        self.mic_source = ctk.StringVar(value="nao")
        self.level = ctk.StringVar(value="1")
        self.all_words_for_level = []
        self.available_words = []

        logo_image = ctk.CTkImage(
            light_image=Image.open("assets/SOLETRANDO.png"),
            dark_image=Image.open("assets/SOLETRANDO.png"),
            size=(300, 80)
        )
        self.logo_label = ctk.CTkLabel(self, image=logo_image, text="")
        self.logo_label.pack(pady=20)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (TelaConexao, TelaInicio, TelaSoletrar, TelaResultado):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_tela(TelaConexao)

    def mostrar_tela(self, tela_class):
        frame = self.frames[tela_class]
        frame.tkraise()

    def connect_nao(self, ip):
        connection = NaoConnection(ip=ip, port=NAO_PORT)
        if connection.session:
            self.nao_commands = NaoCommands(connection)
            self.nao_commands.say("Olá! Estou pronto para o jogo de soletrar.")
            self.nao_commands.subscribe_to_touch_events(
                left_callback=self.handle_left_touch, 
                right_callback=self.handle_right_touch
            )
            self.mostrar_tela(TelaInicio)
            return True
        else:
            connection.close()
            return False

    def load_words_for_level(self):
        level = self.level.get()
        filepath = f"word_lists/{level}_ano.txt"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.all_words_for_level = [line.strip() for line in f if line.strip()]
                self.available_words = self.all_words_for_level.copy()
                random.shuffle(self.available_words)
            self.start_new_round()
        except FileNotFoundError:
            self.frames[TelaInicio].show_error(f"Arquivo de palavras não encontrado: {filepath}")

    def handle_left_touch(self):
        if self.frames[TelaSoletrar].winfo_ismapped():
            self.user_spelling = ""
            self.after(0, self.frames[TelaSoletrar].clear_spelled_letters)
            self.nao_commands.say("Palavra apagada")

    def handle_right_touch(self):
        if self.frames[TelaSoletrar].winfo_ismapped():
            self.nao_commands.say("Confirmado")
            self.after(0, self.finalize_check)

    def start_new_round(self):
        if not self.available_words:
            self.nao_commands.say("Parabéns! Você completou todas as palavras do nível! Recomeçando.")
            self.available_words = self.all_words_for_level.copy()
            random.shuffle(self.available_words)

        self.user_spelling = ""
        self.current_word = self.available_words.pop() 
        
        emoji_hint = EMOJI_MAP.get(self.current_word.lower(), "")

        self.frames[TelaSoletrar].update_word_display(self.current_word)
        self.frames[TelaSoletrar].update_emoji(emoji_hint)
        self.frames[TelaSoletrar].clear_spelled_letters()
        self.nao_commands.say(f"A nova palavra é: {self.current_word}")
        self.mostrar_tela(TelaSoletrar)

    def start_voice_spelling(self):
        source = self.mic_source.get()
        self.frames[TelaSoletrar].set_status(f"Ouvindo pelo {source.upper()}...", "white")
        
        threading.Thread(
            target=self.nao_commands.start_listening_for_spelling,
            args=(self.update_spelling_from_thread, self.check_spelling_from_thread, source),
            daemon=True
        ).start()

    def update_spelling_from_thread(self, spelling):
        self.user_spelling = spelling
        self.after(0, self.frames[TelaSoletrar].update_spelled_letters, self.user_spelling)

    def check_spelling_from_thread(self, final_spelling):
        self.user_spelling = final_spelling
        self.after(0, self.finalize_check)

    def finalize_check(self):
        self.frames[TelaSoletrar].update_spelled_letters(self.user_spelling)

        normalized_spelling = self.user_spelling.lower().replace(" ", "")
        normalized_word = self.current_word.lower()

        if normalized_spelling == normalized_word:
            result_text = "Parabéns, você acertou!"
            self.nao_commands.say(result_text)
        else:
            result_text = f"Você errou! A palavra era '{self.current_word.upper()}'"
            self.nao_commands.say(f"Que pena, você errou. A palavra correta era {self.current_word}")
        
        self.frames[TelaResultado].set_result(self.current_word, self.user_spelling, normalized_spelling == normalized_word)
        self.mostrar_tela(TelaResultado)

    def on_closing(self):
        if self.nao_commands:
            self.nao_commands.close()
        self.destroy()


class TelaConexao(ctk.CTkFrame):
    def __init__(self, parent, controller: SoletrandoApp):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="Digite o IP do robô NAO:", font=ctk.CTkFont(size=20))
        self.label.pack(pady=(120, 10))

        self.ip_entry = ctk.CTkEntry(self, placeholder_text="Ex: 192.168.1.10", width=250, font=ctk.CTkFont(size=16))
        self.ip_entry.pack(pady=10)
        self.ip_entry.focus()

        self.connect_button = ctk.CTkButton(self, text="Conectar", command=self.conectar, font=ctk.CTkFont(size=16), height=40)
        self.connect_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=10)
        
        self.controller.bind("<Return>", lambda event: self.conectar())

    def conectar(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            self.status_label.configure(text="O campo de IP não pode estar vazio.", text_color="yellow")
            return

        self.status_label.configure(text=f"Conectando a {ip}...", text_color="white")
        self.update_idletasks()

        if self.controller.connect_nao(ip):
            self.status_label.configure(text="Conectado com sucesso!", text_color="#2ECC71")
        else:
            self.status_label.configure(text="Falha na conexão. Verifique o IP.", text_color="#E74C3C")


class TelaInicio(ctk.CTkFrame):
    def __init__(self, parent, controller: SoletrandoApp):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.label = ctk.CTkLabel(self, text="Tudo pronto para começar!", font=ctk.CTkFont(size=24, weight="bold")
        self.label.pack(pady=(40, 20))

        self.level_label = ctk.CTkLabel(self, text="Escolha o nível (ano escolar):", font=ctk.CTkFont(size=16))
        self.level_label.pack(pady=(10,5))
        self.level_selector = ctk.CTkSegmentedButton(
            self, values=[str(i) for i in range(1, 7)],
            variable=self.controller.level
        )
        self.level_selector.pack(pady=10)

        self.mic_label = ctk.CTkLabel(self, text="Escolha o microfone:", font=ctk.CTkFont(size=16))
        self.mic_label.pack(pady=(10,5))
        self.mic_selector = ctk.CTkSegmentedButton(
            self, values=["NAO", "PC"],
            command=lambda value: self.controller.mic_source.set(value.lower())
        )
        self.mic_selector.set("NAO")
        self.mic_selector.pack(pady=10)

        self.start_button = ctk.CTkButton(self, text="Iniciar Jogo", command=self.controller.load_words_for_level, font=ctk.CTkFont(size=18), height=50)
        self.start_button.pack(pady=30)

        self.error_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14), text_color="#E74C3C")
        self.error_label.pack(pady=10)

    def show_error(self, message):
        self.error_label.configure(text=message)


class TelaSoletrar(ctk.CTkFrame):
    def __init__(self, parent, controller: SoletrandoApp):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.word_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=22, weight="bold")
        self.word_label.pack(pady=(5, 5))

        self.emoji_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=60))
        self.emoji_label.pack(pady=5)

        self.spelled_word_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        self.spelled_word_frame.pack(pady=10, padx=20, fill="x")

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16))
        self.status_label.pack(pady=10)

        self.spell_button = ctk.CTkButton(self, text="Soletrar por Voz", command=self.controller.start_voice_spelling, font=ctk.CTkFont(size=16), height=40)
        self.spell_button.pack(pady=10)

        self.new_word_button = ctk.CTkButton(self, text="Outra Palavra", command=self.controller.start_new_round, font=ctk.CTkFont(size=16), height=40)
        self.new_word_button.pack(pady=10)

    def update_word_display(self, word):
        self.word_label.configure(text=f"A palavra é: {word.upper()}")
        self.spell_button.configure(state="normal")
        self.new_word_button.configure(state="normal")
        self.status_label.configure(text="")

    def update_emoji(self, emoji_char):
        self.emoji_label.configure(text=emoji_char)

    def update_spelled_letters(self, spelling):
        for widget in self.spelled_word_frame.winfo_children():
            widget.destroy()

        inner_frame = ctk.CTkFrame(self.spelled_word_frame, fg_color="transparent")
        inner_frame.pack()

        if not spelling:
            placeholder = ctk.CTkLabel(inner_frame, text="-", font=ctk.CTkFont(size=40, weight="bold"), text_color="gray")
            placeholder.pack()
        else:
            for letter in spelling:
                letter_box = ctk.CTkLabel(
                    inner_frame, text=letter.upper(), 
                    font=ctk.CTkFont(size=35, weight="bold"),
                    fg_color="#34495E", corner_radius=8, width=50, height=50
                )
                letter_box.pack(side="left", padx=5)
    
    def clear_spelled_letters(self):
        self.update_spelled_letters("")

    def set_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)
        self.spell_button.configure(state="disabled")
        self.new_word_button.configure(state="disabled")


class TelaResultado(ctk.CTkFrame):
    def __init__(self, parent, controller: SoletrandoApp):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.result_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=24, weight="bold")
        self.result_label.pack(pady=(80, 20))

        self.word_info_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18))
        self.word_info_label.pack(pady=10)

        self.play_again_button = ctk.CTkButton(self, text="Jogar Novamente", command=self.controller.start_new_round, font=ctk.CTkFont(size=16), height=40)
        self.play_again_button.pack(pady=20)

    def set_result(self, correct_word, spelled_word, is_correct):
        if is_correct:
            self.result_label.configure(text="VOCÊ ACERTOU!", text_color="#2ECC71")
            self.word_info_label.configure(text=f"A palavra era: {correct_word.upper()}")
        else:
            self.result_label.configure(text="VOCÊ ERROU!", text_color="#E74C3C")
            self.word_info_label.configure(text=f"Correto: {correct_word.upper()}\nVocê soletrou: {spelled_word.upper()}")


if __name__ == "__main__":
    app = SoletrandoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()