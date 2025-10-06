"""Módulo para o painel de conexão com o NAO."""
import customtkinter as ctk

class PainelNAO(ctk.CTkFrame):
    """Frame para exibir e controlar a conexão com o robô NAO."""
    def __init__(self, master, callback_conectar, callback_desconectar):
        super().__init__(master, fg_color="#2A2D2E", corner_radius=10)

        self.callback_conectar = callback_conectar
        self.callback_desconectar = callback_desconectar

        self.label = ctk.CTkLabel(self, text="Robô NAO", font=ctk.CTkFont(weight="bold"))
        self.label.pack(pady=5, padx=10)

        self.entry_ip = ctk.CTkEntry(self, placeholder_text="Endereço IP do NAO")
        self.entry_ip.pack(pady=5, padx=10)

        self.btn_conectar = ctk.CTkButton(self, text="Conectar", command=self._conectar)
        self.btn_conectar.pack(pady=5, padx=10)

        self.btn_desconectar = ctk.CTkButton(self, text="Desconectar", command=self.callback_desconectar, state="disabled")
        self.btn_desconectar.pack(pady=5, padx=10)

        self.status_label = ctk.CTkLabel(self, text="Status: Desconectado", text_color="#E74C3C")
        self.status_label.pack(pady=5, padx=10)

    def _conectar(self):
        ip = self.entry_ip.get()
        if ip:
            self.callback_conectar(ip)

    def atualizar_status(self, conectado: bool, ip: str = ""):
        """Atualiza a UI para refletir o status da conexão."""
        if conectado:
            self.status_label.configure(text=f"Conectado a {ip}", text_color="#2ECC71")
            self.btn_conectar.configure(state="disabled")
            self.entry_ip.configure(state="disabled")
            self.btn_desconectar.configure(state="normal")
        else:
            self.status_label.configure(text="Status: Desconectado", text_color="#E74C3C")
            self.btn_conectar.configure(state="normal")
            self.entry_ip.configure(state="normal")
            self.btn_desconectar.configure(state="disabled")
