import json
import os
import zipfile
from tkinter import messagebox

import customtkinter as ctk
import gdown
from ui.components.game_store_card import GameStoreCard
from ui.components.search_input import SearchInput
from utils.utils import get_rom_path, load_icons


def build_store_drawer(frame, refresh_callback=None):
    """Constrói o drawer da loja de jogos com busca e listagem."""
    # --- Limpa o conteúdo existente ---
    for w in frame.winfo_children():
        w.destroy()

    frame.configure(fg_color="#121212")

    # --- Ícones e cores ---
    icons = load_icons()

    # --- HEADER ---
    header = ctk.CTkFrame(frame, fg_color="#121212", height=70)
    header.pack(fill="x", pady=(10, 0))
    header.pack_propagate(False)

    header_inner = ctk.CTkFrame(header, fg_color="transparent")
    header_inner.pack(fill="x", expand=True, padx=20, pady=10)

    # =========================================================
    # 🧩 Função: Atualizar lista de jogos (download do Drive)
    # =========================================================
    def atualizar_lista_drive():
        """Baixa e atualiza o arquivo games.json a partir do Google Drive."""
        try:
            rom_dir = get_rom_path("")
            zip_path = os.path.join(rom_dir, "games.zip")

            update_log("🔄 Atualizando lista de jogos...")

            file_id = "1kK8h2n9696iZH9pN5HV2KTIwYHj5W2p3"
            url = f"https://drive.google.com/uc?id={file_id}"

            # Baixar o arquivo ZIP
            gdown.download(url, zip_path, quiet=False, fuzzy=True)

            if not os.path.exists(zip_path):
                raise FileNotFoundError("Falha ao baixar o arquivo games.zip")

            # Extrair o JSON dentro de /roms
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(rom_dir)
            os.remove(zip_path)

            update_log("✅ Lista de jogos atualizada com sucesso!")

            # Recarregar lista após atualização
            nonlocal all_games
            all_games = carregar_lista_local()
            buscar_e_listar()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao atualizar lista de jogos:\n{e}")

    # --- Input de busca (usando SearchInput) ---
    def on_search_change(text: str):
        buscar_e_listar(text)

    search_input = SearchInput(
        header_inner,
        on_change=on_search_change,
        on_refresh=atualizar_lista_drive,  # <-- callback do refresh agora funcional
    )
    search_input.pack(side="left", fill="x", expand=True)

    # --- SCROLL CONTAINER ---
    frame_scroll = ctk.CTkScrollableFrame(frame, fg_color="#121212", corner_radius=12)
    frame_scroll.pack(fill="both", expand=True, padx=10, pady=5)

    # --- LABEL DE STATUS ---
    status_label = ctk.CTkLabel(frame, text="", font=("Segoe UI", 12), text_color="gray")
    status_label.pack(pady=(4, 4))

    def update_log(msg):
        status_label.configure(text=msg)
        status_label.update_idletasks()

    # --- CARREGAR LISTA DE JOGOS ---
    def carregar_lista_local():
        try:
            json_path = os.path.join(get_rom_path(""), "games.json")

            if not os.path.exists(json_path):
                messagebox.showerror(
                    "Erro", "O arquivo games.json não foi encontrado na pasta /roms."
                )
                return []

            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                messagebox.showerror("Erro", "O arquivo games.json está em formato inválido.")
                return []

            validos = [j for j in data if all(k in j for k in ("game", "name", "size"))]
            return validos

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar games.json:\n{e}")
            return []

    # --- RENDERIZAR JOGOS ---
    def renderizar_lista(jogos):
        for widget in frame_scroll.winfo_children():
            widget.destroy()

        if not jogos:
            ctk.CTkLabel(
                frame_scroll,
                text="Nenhum jogo encontrado.",
                font=("Segoe UI", 14),
                text_color="#888",
            ).pack(pady=20)
            return

        for jogo in jogos:
            GameStoreCard(frame_scroll, jogo, icons, update_log, refresh_callback)

    # --- BUSCAR E LISTAR ---
    all_games = carregar_lista_local()

    def buscar_e_listar(filtro_text=""):
        filtro = filtro_text.strip().lower()
        filtrados = [j for j in all_games if filtro in j.get("name", "").lower()]
        status_label.configure(text=f"{len(filtrados)} jogo(s) encontrado(s)")
        renderizar_lista(filtrados)

    # --- Render inicial ---
    buscar_e_listar()
