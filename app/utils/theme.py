import os

import customtkinter as ctk
from utils.utils import get_asset_path

# 🎨 CORES PRINCIPAIS
PRIMARY_COLOR = "#8f4cff"  # Roxo principal
PRIMARY_HOVER = "#a866ff"  # Hover / destaque
SURFACE_HOVER = "#3D3D3D"
BACKGROUND = "#202020"
BACKGROUND_DARK = "#121212"  # Fundo base
SURFACE = "#1e1e1e"  # Containers, frames
SURFACE_LIGHT = "#2b2b2b"  # Barras, inputs, etc
TEXT_PRIMARY = "#ffffff"  # Texto principal
TEXT_SECONDARY = "#aaaaaa"  # Texto secundário
TEXT_MUTED = "#777777"  # Texto apagado
SUCCESS = "#50fa7b"  # Verde de sucesso
ERROR = "#ff5555"  # Vermelho
CLEAR= "#eba8a8"
WARNING = "#f1fa8c"  # Amarelo
TRANSPARENT = "transparent"  # Transparente

# 🧱 ESPAÇAMENTOS E BORDAS
RADIUS = 10
PADDING = 10
SPACING = 8

# 🖋️ FONTES
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SM = 12
FONT_SIZE_MD = 14
FONT_SIZE_LG = 18
FONT_WEIGHT_BOLD = "bold"
TITLE_GAME = (FONT_FAMILY, FONT_SIZE_SM, FONT_WEIGHT_BOLD)


def create_window(
    parent=None,
    title: str = "Axis",
    width: int = 1000,
    height: int = 800,
    min_width: int = 800,
    min_height: int = 600,
    resizable: bool = True,
    fullscreen: bool = False,
    bg: str = BACKGROUND
):
    """
    Cria uma janela CTk padronizada.
    Se um 'parent' for passado, cria um CTkToplevel (janela filha).
    Caso contrário, cria uma janela principal (CTk).
    """

    # === Define o tipo de janela ===
    if parent:
        root = ctk.CTkToplevel(parent)
    else:
        root = ctk.CTk()

    ctk.set_appearance_mode("dark")
    root.title(title)
    root.configure(fg_color=bg)

    # === Centraliza a janela ===
    def center_window():
        root.update_idletasks()
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

    if fullscreen:
        root.attributes("-fullscreen", True)
    else:
        center_window()

    root.minsize(min_width, min_height)
    root.resizable(resizable, resizable)

    # === Ícone ===
    try:
        icon_path = get_asset_path("icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
        else:
            alt_icon = get_asset_path("icon.png")
            if os.path.exists(alt_icon):
                from PIL import Image, ImageTk

                icon_img = Image.open(alt_icon)
                root.iconphoto(False, ImageTk.PhotoImage(icon_img))
    except Exception as e:
        print(f"[WARN] Falha ao aplicar ícone: {e}")

    # === Se for janela filha ===
    if parent:
        root.transient(parent)
        root.grab_set()
        root.focus_force()
        root.lift()
        root.attributes("-topmost", True)
        root.after(200, lambda: root.attributes("-topmost", False))
        root.iconbitmap(get_asset_path("icon.ico"))

    return root
