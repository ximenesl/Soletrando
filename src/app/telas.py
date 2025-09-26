"""Módulo com as telas (frames) da aplicação."""
import customtkinter as ctk

class TelaSoletrar(ctk.CTkFrame):
    """Frame principal onde o jogo de soletração acontece."""
    def __init__(self, parent, app_callbacks):
        super().__init__(parent, fg_color="transparent")
        self.app_callbacks = app_callbacks

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Widgets --- #
        self.palavra_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=28, weight="bold"))
        self.palavra_label.grid(row=0, column=0, pady=(20, 10))

        self.frame_letras_soletradas = ctk.CTkFrame(self, fg_color="transparent", height=80)
        self.frame_letras_soletradas.grid(row=1, column=0, pady=10, padx=20, sticky="n")

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=18))
        self.status_label.grid(row=2, column=0, pady=10)

        # --- Botões de Ação ---
        botoes_frame = ctk.CTkFrame(self, fg_color="transparent")
        botoes_frame.grid(row=3, column=0, pady=20)

        self.botao_soletrar = ctk.CTkButton(botoes_frame, text="Soletrar por Voz", command=self.app_callbacks["iniciar_soletracao"], height=40)
        self.botao_soletrar.pack(side="left", padx=10)

        self.botao_confirmar = ctk.CTkButton(botoes_frame, text="Confirmar", command=self.app_callbacks["finalizar_verificacao"], height=40)
        self.botao_confirmar.pack(side="left", padx=10)

        self.botao_outra_palavra = ctk.CTkButton(botoes_frame, text="Pular Palavra", command=self.app_callbacks["iniciar_nova_rodada"], height=40)
        self.botao_outra_palavra.pack(side="left", padx=10)

    def atualizar_exibicao_palavra(self, palavra: str):
        self.palavra_label.configure(text=f"A palavra é: {palavra.upper()}")
        self.limpar_letras_soletradas()

    def atualizar_letras_soletradas(self, soletracao: str):
        for widget in self.frame_letras_soletradas.winfo_children():
            widget.destroy()

        frame_interno = ctk.CTkFrame(self.frame_letras_soletradas, fg_color="transparent")
        frame_interno.pack()

        if not soletracao:
            placeholder = ctk.CTkLabel(frame_interno, text="-", font=ctk.CTkFont(size=40, weight="bold"), text_color="gray")
            placeholder.pack()
        else:
            for letra in soletracao:
                caixa_letra = ctk.CTkLabel(
                    frame_interno, text=letra.upper(), 
                    font=ctk.CTkFont(size=35, weight="bold"),
                    fg_color="#34495E", corner_radius=8, width=50, height=50
                )
                caixa_letra.pack(side="left", padx=5)

    def limpar_letras_soletradas(self):
        self.atualizar_letras_soletradas("")

    def definir_status(self, texto: str, cor: str = "white"):
        self.status_label.configure(text=texto, text_color=cor)

    def configurar_estado_botoes(self, estado: str):
        """Altera o estado dos botões (normal, disabled)."""
        self.botao_soletrar.configure(state=estado)
        self.botao_confirmar.configure(state=estado)
        self.botao_outra_palavra.configure(state=estado)


class TelaResultado(ctk.CTkFrame):
    """Frame para mostrar o resultado de uma rodada."""
    def __init__(self, parent, app_callbacks):
        super().__init__(parent, fg_color="transparent")
        self.app_callbacks = app_callbacks

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        self.resultado_label = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=32, weight="bold"))
        self.resultado_label.pack(pady=(20, 10))

        self.info_palavra_label = ctk.CTkLabel(container, text="", font=ctk.CTkFont(size=20))
        self.info_palavra_label.pack(pady=10)

        self.botao_jogar_novamente = ctk.CTkButton(container, text="Próxima Palavra", command=self.app_callbacks["iniciar_nova_rodada"], height=40)
        self.botao_jogar_novamente.pack(pady=20)

    def definir_resultado(self, palavra_correta: str, soletracao_usuario: str, acertou: bool):
        if acertou:
            self.resultado_label.configure(text="VOCÊ ACERTOU!", text_color="#2ECC71")
            self.info_palavra_label.configure(text=f"A palavra era: {palavra_correta.upper()}")
        else:
            self.resultado_label.configure(text="VOCÊ ERROU!", text_color="#E74C3C")
            self.info_palavra_label.configure(text=f"Correto: {palavra_correta.upper()}\nVocê soletrou: {soletracao_usuario.upper()}")
