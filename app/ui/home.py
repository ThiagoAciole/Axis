import customtkinter as ctk
from ui.components.footer import create_footer
from ui.components.game_card import GameCard
from ui.components.search_input import SearchInput
from ui.control_settings import ControlSettings
from ui.store import build_store_drawer
from utils.theme import *
from utils.utils import alterar_capa, encontrar_jogos, excluir_jogo, iniciar_jogo_ps1, load_icons

root = None
game_frame = None
imagens = []


# === Atualiza lista de jogos ===
def refresh_callback():
    exibir_jogos(encontrar_jogos())


# === Exibe jogos dinamicamente ===
def exibir_jogos(lista, colunas=6):
    global imagens
    imagens = []

    for w in game_frame.winfo_children():
        w.destroy()

    scroll = ctk.CTkScrollableFrame(game_frame, fg_color=BACKGROUND_DARK)
    scroll.pack(fill="both", expand=True)

    if not lista:
        ctk.CTkLabel(
            scroll,
            text="Nenhum jogo encontrado!",
            text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, FONT_SIZE_LG, FONT_WEIGHT_BOLD),
        ).pack(pady=50)
        return

    for idx, item in enumerate(lista):
        card = GameCard(
            parent=scroll,
            title=item["title"],
            image=item["image"],
            platform="ps2",
            on_click=lambda f=item["file"]: iniciar_jogo_ps1(f),
            on_edit=lambda f=item["title"]: alterar_capa(f, refresh_callback),
            on_delete=lambda f=item["title"]: excluir_jogo(f, refresh_callback),
        )
        card.grid(row=idx // colunas, column=idx % colunas, padx=10, pady=10)


def open_control_settings():
    ControlSettings(root)


# === Tela principal ===
def start_home():
    global root, game_frame
    root = create_window(title="Axis")

    # === Ícones ===
    icons = load_icons()
    icon_refresh = icons["refresh"]
    icon_download = icons["store"]
    icon_config = icons["config"]

    # === Estrutura principal ===
    main = ctk.CTkFrame(root, fg_color=BACKGROUND)
    main.pack(fill="both", expand=True, padx=PADDING, pady=PADDING)

    main_frame = ctk.CTkFrame(main, fg_color=BACKGROUND)
    main_frame.pack(fill="both", expand=True)

    conteudo = ctk.CTkFrame(main_frame, fg_color=BACKGROUND)
    conteudo.pack(side="left", fill="both", expand=True)

    # === Header ===
    header = ctk.CTkFrame(conteudo, fg_color=BACKGROUND)
    header.pack(fill="x", padx=10, pady=20)

    # === Campo de busca reutilizável ===
    def filtrar_jogos(termo):
        termo = termo.lower().strip()
        if not termo:
            exibir_jogos(encontrar_jogos())
        else:
            filtrados = [j for j in encontrar_jogos() if termo in j["title"].lower()]
            exibir_jogos(filtrados)

    search_input = SearchInput(header, on_change=filtrar_jogos)
    search_input.pack(side="left", padx=10)

    # === Drawer (loja lateral) ===
    drawer = ctk.CTkFrame(main_frame, fg_color=SURFACE, width=0)
    drawer.pack(side="right", fill="y")
    drawer.pack_propagate(False)
    drawer_visible = False

    def toggle_store_drawer():
        nonlocal drawer_visible
        if not drawer_visible:
            drawer.configure(width=450)
            build_store_drawer(drawer, lambda: exibir_jogos(encontrar_jogos(), colunas=3))
            exibir_jogos(encontrar_jogos(), colunas=3)
        else:
            drawer.configure(width=0)
            for w in drawer.winfo_children():
                w.destroy()
            exibir_jogos(encontrar_jogos(), colunas=6)
        drawer_visible = not drawer_visible
        main_frame.update_idletasks()

   # === Botões do header ===

    def create_icon_button(parent, icon, cmd):
        lbl = ctk.CTkLabel(parent, text="", image=icon, fg_color="transparent", cursor="hand2")
        lbl.pack(side="right", padx=8)
        lbl.bind("<Button-1>", lambda e: cmd())

    # Botão de download (fica fora do frame)
    create_icon_button(header, icon_download, toggle_store_drawer)

    # Frame para botões de config e refresh
    config_frame = ctk.CTkFrame(
        header,
        fg_color="#2A2A2A",      # Fundo diferente
        corner_radius=8,
    )
    config_frame.pack(side="right", padx=(0, 10), pady=4)

    # Botões dentro do frame
    create_icon_button(config_frame, icon_config, open_control_settings)
    create_icon_button(config_frame, icon_refresh, lambda: exibir_jogos(encontrar_jogos()))
    
    
    # === Título da seção ===
    ctk.CTkLabel(
        conteudo,
        text="Jogos",
        font=(FONT_FAMILY, FONT_SIZE_LG, FONT_WEIGHT_BOLD),
        text_color=TEXT_PRIMARY,
    ).pack(anchor="w", padx=20, pady=(10, 10))

    # === Área principal dos jogos ===
    game_frame = ctk.CTkFrame(conteudo, fg_color=BACKGROUND)
    game_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

    # === Render inicial ===
    exibir_jogos(encontrar_jogos())

    # === Rodapé ===
    create_footer(root)

    root.mainloop()
