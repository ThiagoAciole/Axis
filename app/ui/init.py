import os
import threading

import customtkinter as ctk
from PIL import Image
from ui.home import start_home
from utils.theme import *
from utils.utils import get_asset_path, get_capa_path, get_rom_path, preparar_emulador


def start_init():
    tela = create_window(
        title="Axis",
        width=600,
        height=400,
        min_width=600,
        min_height=400,
        resizable=False,
    )
    # === CONTAINER PRINCIPAL ===
    container = ctk.CTkFrame(tela, fg_color=TRANSPARENT)
    container.pack(expand=True, fill="both")

    # === LOGO CENTRAL ===
    logo_path = get_asset_path("logo.png")
    if os.path.exists(logo_path):
        logo_img = ctk.CTkImage(Image.open(logo_path), size=(140, 140))
        ctk.CTkLabel(container, image=logo_img, text="").pack(expand=True, pady=(40, 10))
    else:
        ctk.CTkLabel(
            container,
            text="PSLabz",
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            text_color=PRIMARY_COLOR,
        ).pack(expand=True, pady=(40, 10))

    # === STATUS LABEL ===
    status_label = ctk.CTkLabel(
        container, text="", text_color=TEXT_PRIMARY, font=(FONT_FAMILY, FONT_SIZE_MD)
    )
    status_label.pack(pady=(10, 8))

    # === PROGRESS BAR ===
    progressbar = ctk.CTkProgressBar(
        container,
        width=400,
        height=6,
        corner_radius=20,
        fg_color=SURFACE_LIGHT,
        progress_color=PRIMARY_COLOR,
        mode="indeterminate",
    )
    progressbar.pack(pady=(0, 20))
    progressbar.start()

    # === Atualizações visuais ===
    def update_progress(value):
        tela.after(0, lambda: progressbar.set(value))

    def update_status(text):
        tela.after(0, lambda: status_label.configure(text=text))

    # === Fluxo de inicialização ===
    def preparar():
        os.makedirs(get_rom_path(""), exist_ok=True)
        os.makedirs(get_capa_path(""), exist_ok=True)
        preparar_emulador(progress_callback=update_progress, status_callback=update_status)

        def fechar_tela():
            try:
                progressbar.stop()
            except:
                pass
            try:
                for after_id in tela.tk.call("after", "info"):
                    tela.after_cancel(after_id)
            except:
                pass
            if tela.winfo_exists():
                tela.destroy()
            start_home()

        tela.after(1000, fechar_tela)

    threading.Thread(target=preparar, daemon=True).start()
    tela.mainloop()


if __name__ == "__main__":
    start_init()
