"""Módulo para o painel de conexão com o NAO."""
import customtkinter as ctk

class PainelNAO(ctk.CTkFrame):
    """Frame para exibir e controlar a conexão com o robô NAO."""
    def __init__(self, parent, callback_conectar, callback_desconectar):
        super().__init__(parent, corner_radius=10, fg_color="#2A2D2E")
        self.callback_conectar = callback_conectar
        self.callback_desconectar = callback_desconectar

        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text="Robô NAO", font=ctk.CTkFont(weight="bold"))
        self.label.grid(row=0, column=0, columnspan=3, padx=10, pady=(5, 0), sticky="ew")

        self.ip_entry = ctk.CTkEntry(self, placeholder_text="192.168.1.1")
        self.ip_entry.grid(row=1, column=0, columnspan=2, padx=(10, 5), pady=5, sticky="ew")

        self.status_led = ctk.CTkLabel(self, text="", width=20, height=20, fg_color="gray", corner_radius=10)
        self.status_led.grid(row=1, column=2, padx=(0, 10), pady=5)

        self.connect_button = ctk.CTkButton(self, text="Conectar", command=self._conectar, height=25)
        self.connect_button.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="ew")

        self.disconnect_button = ctk.CTkButton(self, text="Desconectar", command=self._desconectar, height=25, state="disabled")
        self.disconnect_button.grid(row=2, column=1, columnspan=2, padx=(0, 10), pady=(0, 10), sticky="ew")

    def _conectar(self):
        ip = self.ip_entry.get().strip()
        if ip:
            self.callback_conectar(ip)

    def _desconectar(self):
        self.callback_desconectar()

    def atualizar_status(self, conectado: bool, ip: str | None = None):
        """Atualiza a UI para refletir o status da conexão."""
        if conectado:
            self.status_led.configure(fg_color="#2ECC71") # Verde
            self.ip_entry.delete(0, ctk.END)
            if ip:
                self.ip_entry.insert(0, ip)
            self.ip_entry.configure(state="disabled")
            self.connect_button.configure(state="disabled")
            self.disconnect_button.configure(state="normal")
        else:
            self.status_led.configure(fg_color="gray")
            self.ip_entry.configure(state="normal")
            self.connect_button.configure(state="normal")
            self.disconnect_button.configure(state="disabled")
