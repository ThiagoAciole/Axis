import os

import customtkinter as ctk
from utils.download import baixar_jogo


class GameStoreCard(ctk.CTkFrame):

    def __init__(self, parent, jogo, icons, update_log, refresh_callback):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=10, height=70)
        self.pack(fill="x", pady=6, padx=10)
        self.pack_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.nome = jogo.get("name", "Sem nome")
        self.link = jogo.get("game", "")
        self.capa = jogo.get("cover", "")
        self.tamanho = jogo.get("size", "")
        self.icons = icons
        self.update_log = update_log
        self.refresh_callback = refresh_callback

        # === Info ===
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=15, pady=(8, 8))

        ctk.CTkLabel(
            info_frame, text=self.nome, font=("Segoe UI", 14, "bold"), text_color="white"
        ).pack(anchor="w")
        if self.tamanho:
            ctk.CTkLabel(
                info_frame, text=self.tamanho, font=("Segoe UI", 12), text_color="#aaa"
            ).pack(anchor="w", pady=(0, 2))

        # === Botão ===
        from utils.utils import get_rom_path  # import interno para evitar ciclos

        roms_existentes = {
            os.path.splitext(f)[0]
            for f in os.listdir(get_rom_path(""))
            if f.lower().endswith(".chd")
        }

        baixado = self.nome in roms_existentes
        self.btn = ctk.CTkButton(
            self,
            text="",
            image=self.icons["check"] if baixado else self.icons["download"],
            width=40,
            height=30,
            fg_color="transparent",
        )
        self.btn.grid(row=0, column=1, padx=(0, 20))

        if not baixado:
            self.btn.configure(command=self._baixar)
        else:
            self.btn.configure(state="disabled")

    # === Função de download ===
    def _baixar(self):
        jogo = {
            "name": self.nome,
            "game": self.link,
            "cover": self.capa,
            "size": self.tamanho or "0 MB",
        }

        baixar_jogo(
            jogo,
            self.btn,
            self.update_log,
            self.refresh_callback,
            self,
            self.icons["check"],
        )
