"""Arquivo principal da aplicação Soletrando com NAO."""
import customtkinter as ctk
from PIL import Image
from config.settings import ARQUIVO_LOGO
from app.controlador_jogo import ControladorJogo
from app.telas import TelaSoletrar, TelaResultado
from app.painel_nao import PainelNAO

class AppSoletrando(ctk.CTk):
    """Classe principal da aplicação."""
    def __init__(self):
        super().__init__()
        self.title("Soletrando com NAO")
        self.geometry("700x650")
        self.minsize(700, 650)
        self.resizable(True, True)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#0077CC")

        self.protocol("WM_DELETE_WINDOW", self.fechar)

        # --- Controlador ---
        self.controlador = ControladorJogo(self)

        # --- Layout Principal ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Logo ---
        logo_image = ctk.CTkImage(Image.open(ARQUIVO_LOGO), size=(300, 80))
        logo_label = ctk.CTkLabel(self, image=logo_image, text="")
        logo_label.grid(row=0, column=0, pady=10)

        # --- Container das Telas (ocupa o espaço central e expande) ---
        container_central = ctk.CTkFrame(self, fg_color="transparent")
        container_central.grid(row=1, column=0, sticky="nsew")
        container_central.grid_rowconfigure(0, weight=1)
        container_central.grid_columnconfigure(0, weight=1)

        self.telas = {}
        callbacks = {
            "iniciar_soletracao": self.controlador.iniciar_soletracao,
            "finalizar_verificacao": self.controlador.finalizar_verificacao,
            "iniciar_nova_rodada": self.controlador.iniciar_nova_rodada
        }

        self.tela_soletrar = TelaSoletrar(container_central, callbacks)
        self.tela_resultado = TelaResultado(container_central, callbacks)

        self.telas["soletrar"] = self.tela_soletrar
        self.telas["resultado"] = self.tela_resultado

        # As telas não se expandem, ficam centralizadas no container
        self.tela_soletrar.grid(row=0, column=0, sticky="")
        self.tela_resultado.grid(row=0, column=0, sticky="")

        # --- Painel de Conexão NAO ---
        self.painel_nao = PainelNAO(self, self.controlador.conectar_nao, self.controlador.desconectar_nao)
        self.painel_nao.place(x=10, y=10, anchor="nw")

        # --- Controles do Jogo (Nível e Microfone) ---
        controles_frame = ctk.CTkFrame(self, fg_color="#2A2D2E", corner_radius=10)
        controles_frame.place(relx=0.99, y=10, anchor="ne")

        ctk.CTkLabel(controles_frame, text="Nível:").pack(padx=10, pady=(5,0))
        self.seletor_nivel = ctk.CTkSegmentedButton(
            controles_frame, values=[str(i) for i in range(1, 7)],
            command=self.controlador.definir_nivel
        )
        self.seletor_nivel.set(self.controlador.nivel_atual)
        self.seletor_nivel.pack(padx=10, pady=(0,10))

        ctk.CTkLabel(controles_frame, text="Microfone:").pack(padx=10, pady=(5,0))
        self.seletor_mic = ctk.CTkSegmentedButton(
            controles_frame, values=["PC", "NAO"],
            command=self.controlador.definir_fonte_microfone
        )
        self.seletor_mic.set(self.controlador.fonte_microfone.upper())
        self.seletor_mic.pack(padx=10, pady=(0,10))

        # Inicia o jogo
        self.controlador.iniciar_jogo()

    def mudar_para_tela(self, nome_tela: str):
        """Mostra a tela solicitada."""
        tela = self.telas.get(nome_tela)
        if tela:
            tela.tkraise()

    def mostrar_erro(self, mensagem: str):
        """Exibe uma mensagem de erro na tela de soletração."""
        self.tela_soletrar.definir_status(mensagem, "#E74C3C")

    def definir_selecao_mic(self, mic: str):
        """Atualiza a seleção do botão de microfone na UI."""
        self.seletor_mic.set(mic.upper())

    def fechar(self):
        """Método chamado ao fechar a janela."""
        self.controlador.fechar_aplicacao()

if __name__ == "__main__":
    app = AppSoletrando()
    app.mainloop()