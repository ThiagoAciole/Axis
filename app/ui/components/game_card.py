import os

import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image, ImageOps
from utils.theme import *
from utils.utils import get_asset_path, get_capa_path, load_icons


class GameCard(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        title: str,
        image: str,
        platform: str = "ps2",
        on_click=None,
        on_edit=None,
        on_delete=None,
        width=120,
        height=130,
        *args,
        **kwargs,
    ):
        super().__init__(
            parent,
            fg_color=BACKGROUND_DARK,
            corner_radius=8,
            width=width + 22,
            height=height + 40,
        )

        self.pack_propagate(False)
        self.title = title
        self.image = image
        self.platform = platform
        self.on_click = on_click
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.root = self.winfo_toplevel()

        # === Caminhos ===
        capa_path = get_capa_path(self.image)
        if not os.path.exists(capa_path):
            capa_path = get_capa_path("default.png")

        mold_path = get_asset_path("ps1_path.png")
        if not os.path.exists(mold_path):
            raise FileNotFoundError(f"Moldura não encontrada: {mold_path}")

        # === Carrega imagens ===
        capa = Image.open(capa_path).convert("RGBA")
        moldura = Image.open(mold_path).convert("RGBA")

        # === Redimensiona proporcionalmente (fit) ===
        iw, ih = width - 10, height - 10
        capa_fit = ImageOps.contain(capa, (iw, ih), Image.LANCZOS)

        # === Centraliza a imagem dentro do espaço disponível ===
        composed = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        x = (width - capa_fit.width) // 2
        y = (height - capa_fit.height) // 2
        composed.paste(capa_fit, (x, y))
        moldura = moldura.resize((width, height), Image.LANCZOS)
        composed.paste(moldura, (0, 0), mask=moldura)

        # === Cria imagem final ===
        self.tk_image = CTkImage(light_image=composed, dark_image=composed, size=(width, height))

        # === Texto do card ===
        title_text = title if len(title) <= 18 else title[:15] + "..."

        # === Botão principal ===
        self.button = ctk.CTkButton(
            self,
            image=self.tk_image,
            text=title_text,
            compound="top",
            fg_color=TRANSPARENT,
            hover_color=SURFACE_LIGHT,
            width=width,
            height=height,
            text_color="white",
            font=TITLE_GAME,
            command=self.on_click,
        )
        self.button.pack(expand=True, fill="both")

        # === Bind botão direito ===
        self.button.bind("<Button-3>", self.abrir_menu)

    def abrir_menu(self, event):
        """Menu de contexto (botão direito)."""
        root = self.root
        for w in root.winfo_children():
            if isinstance(w, ctk.CTkFrame) and getattr(w, "is_context_menu", False):
                w.destroy()

        menu = ctk.CTkFrame(root, fg_color=BACKGROUND, corner_radius=8)
        menu.is_context_menu = True

        icons = load_icons()
        icon_edit = icons.get("edit")
        icon_trash = icons.get("trash")

        # === Opções ===
        if self.on_edit:
            ctk.CTkButton(
                menu,
                image=icon_edit,
                text="Alterar Capa do Jogo",
                compound="left",
                font=("Segoe UI", 13, "bold"),
                text_color="white",
                fg_color=BACKGROUND,
                hover_color=SURFACE_LIGHT,
                corner_radius=6,
                width=230,
                height=40,
                anchor="w",
                command=lambda: (menu.destroy(), self.on_edit(self.title)),
            ).pack(padx=1, pady=(6, 3))

        if self.on_delete:
            ctk.CTkButton(
                menu,
                image=icon_trash,
                text="Excluir Jogo",
                compound="left",
                font=("Segoe UI", 13, "bold"),
                text_color="#ff6666",
                fg_color=BACKGROUND,
                hover_color=SURFACE_LIGHT,
                corner_radius=6,
                width=230,
                height=40,
                anchor="w",
                command=lambda: (menu.destroy(), self.on_delete(self.title)),
            ).pack(padx=1, pady=(3, 6))

        # === Posicionamento ===
        widget = event.widget
        widget_x = widget.winfo_rootx() - root.winfo_rootx()
        widget_y = widget.winfo_rooty() - root.winfo_rooty()
        widget_w = widget.winfo_width()
        menu_w = menu.winfo_reqwidth()
        janela_w = root.winfo_width()

        pos_x = (
            max(widget_x - menu_w - 10, 0)
            if widget_x + widget_w + menu_w + 20 > janela_w
            else widget_x + widget_w + 10
        )

        menu.place(x=pos_x, y=widget_y)

        def fechar_menu(ev):
            if not (
                menu.winfo_x()
                <= ev.x_root - root.winfo_rootx()
                <= menu.winfo_x() + menu.winfo_width()
                and menu.winfo_y()
                <= ev.y_root - root.winfo_rooty()
                <= menu.winfo_y() + menu.winfo_height()
            ):
                menu.destroy()
                root.unbind("<Button-1>")

        root.bind("<Button-1>", fechar_menu)
