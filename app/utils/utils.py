# === IMPORTAÇÕES GERAIS ===
import os
import shutil
import subprocess
import sys
import time
import warnings
import zipfile
from tkinter import filedialog, messagebox

import keyboard
import pygame
import requests
from customtkinter import CTkImage
from PIL import Image

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")


# ===========================
# 🔧 CAMINHOS BASE
# ===========================


def get_base_path():
    """Retorna o caminho base da aplicação (raiz do executável ou projeto)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_external_root():
    """Caminho raiz onde ficarão as pastas externas: /roms, /covers, /game"""
    base = get_base_path()
    if base.endswith("app"):
        base = os.path.dirname(base)
    return base


def get_app_path(subdir: str, name: str = ""):
    base = get_base_path()
    return os.path.join(base, subdir, name)


def get_asset_path(name: str = ""):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        path = os.path.join(base, "app", "assets", name)
    else:
        path = os.path.join(os.path.dirname(__file__), "..", "assets", name)
    return os.path.abspath(path)


def get_setting_path(name: str = ""):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        path = os.path.join(base, "app", "settings", name)
    else:
        path = os.path.join(os.path.dirname(__file__), "..", "settings", name)
    return os.path.abspath(path)


def get_icon_path(name: str):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        path = os.path.join(base, "app", "assets", "icons", name)
    else:
        path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", name)
    return os.path.abspath(path)


def get_button_path(name: str):
    """Retorna o caminho absoluto para os ícones dos botões (CIRCLE, CROSS etc.)."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        path = os.path.join(base, "app", "assets", "icons", "buttons", name)
    else:
        path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "buttons", name)
    return os.path.abspath(path)


# ===========================
# 📂 DIRETÓRIOS EXTERNOS
# ===========================


def get_rom_path(name: str = ""):
    root = get_external_root()
    path = os.path.join(root, "roms")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, name)


def get_capa_path(name: str = ""):
    root = get_external_root()
    path = os.path.join(root, "covers")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, name)


def get_emulator_path(name: str = ""):
    root = get_external_root()
    path = os.path.join(root, "game")
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, name)


# ===========================
# ⚙️ ESTRUTURA INICIAL
# ===========================


def preparar_emulador(progress_callback=None, status_callback=None):

    game_dir = get_emulator_path("")
    rom_dir = get_rom_path("")
    capa_dir = get_capa_path("")

    os.makedirs(game_dir, exist_ok=True)
    os.makedirs(rom_dir, exist_ok=True)
    os.makedirs(capa_dir, exist_ok=True)

    try:
        # === Copiar assets e configs ===
        default_src = get_setting_path("default.png")
        default_dest = os.path.join(capa_dir, "default.png")
        if os.path.exists(default_src) and not os.path.exists(default_dest):
            shutil.copy(default_src, default_dest)

        games_src = get_setting_path("games.json")
        games_dest = os.path.join(rom_dir, "games.json")
        if os.path.exists(games_src) and not os.path.exists(games_dest):
            shutil.copy(games_src, games_dest)

        bios_dir = os.path.join(game_dir, "bios")
        os.makedirs(bios_dir, exist_ok=True)
        bios_name = "SCPH1001.BIN"
        bios_src = get_setting_path(bios_name)
        bios_dest = os.path.join(bios_dir, bios_name)
        if os.path.exists(bios_src) and not os.path.exists(bios_dest):
            shutil.copy(bios_src, bios_dest)

        settings_src = get_setting_path("settings.ini")
        settings_dest = os.path.join(game_dir, "settings.ini")
        if os.path.exists(settings_src) and not os.path.exists(settings_dest):
            shutil.copy(settings_src, settings_dest)

        portable_txt = os.path.join(game_dir, "portable.txt")
        if not os.path.exists(portable_txt):
            with open(portable_txt, "w", encoding="utf-8") as f:
                f.write("Portable Mode Enabled\n")

    except Exception as e:
        print(f"[WARN] Falha ao copiar arquivos padrão: {e}")

    # === Verifica DuckStation ===
    duck_exe = next(
        (
            f
            for f in os.listdir(game_dir)
            if f.lower().startswith("duckstation") and f.endswith(".exe")
        ),
        None,
    )
    if duck_exe:
        if status_callback:
            status_callback("")
        return

    # === Baixar DuckStation ===
    if status_callback:
        status_callback("Baixando Arquivos...")

    url = "https://github.com/stenzek/duckstation/releases/latest/download/duckstation-windows-x64-release.zip"
    temp_zip = os.path.join(game_dir, "duckstation.zip")

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            baixado = 0
            with open(temp_zip, "wb") as f:
                for chunk in r.iter_content(1024 * 256):
                    if chunk:
                        f.write(chunk)
                        baixado += len(chunk)
                        if progress_callback and total > 0:
                            progress_callback(baixado / total)

        if status_callback:
            status_callback("Extraindo Arquivos...")

        with zipfile.ZipFile(temp_zip, "r") as z:
            z.extractall(path=game_dir)
        os.remove(temp_zip)

    except Exception as e:
        if status_callback:
            status_callback(f"Erro ao baixar Arquivos: {e}")
        return

    if status_callback:
        status_callback("Axis instalado e pronto")


# ===========================
# 🎮 INICIAR JOGO PS1
# ===========================


def iniciar_jogo_ps1(arquivo):
    try:
        duck_dir = get_emulator_path("")
        duck_exe = next(
            (
                os.path.join(duck_dir, f)
                for f in os.listdir(duck_dir)
                if f.lower().startswith("duckstation") and f.lower().endswith(".exe")
            ),
            None,
        )

        if not duck_exe:
            messagebox.showerror("Erro", "DuckStation não encontrado na pasta /game.")
            return

        rom = get_rom_path(arquivo)
        if not os.path.exists(rom):
            messagebox.showerror("Erro", f"O jogo {arquivo} não foi encontrado em /roms/.")
            return

        # === Inicia o jogo em modo fullscreen ===
        process = subprocess.Popen([duck_exe, "-fullscreen", "-nogui", rom])
        print("[INFO] Jogo iniciado. Pressione ESC ou segure L1 + X por 1s para fechar.")

        # === Inicializa pygame para detectar controle ===
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
            print(f"[INFO] Controle detectado: {joystick.get_name()}")
        else:
            joystick = None
            print("[WARN] Nenhum controle detectado. Só ESC funcionará.")

        # === Controle de tempo de pressionamento ===
        combo_start_time = None
        combo_duration = 1.0  # Segurar por 1 segundo

        # === IDs de botões ===
        BTN_X = 2
        BTN_L1 = 4

        # === Loop de monitoramento ===
        while process.poll() is None:
            # Fecha com ESC no teclado
            if keyboard.is_pressed("esc"):
                print("[INFO] ESC pressionado — encerrando o jogo...")
                process.terminate()
                break

            # Detecta controle
            if joystick:
                pygame.event.pump()
                l1_pressed = joystick.get_button(BTN_L1)
                x_pressed = joystick.get_button(BTN_X)

                if l1_pressed and x_pressed:
                    if combo_start_time is None:
                        combo_start_time = time.time()
                    elif time.time() - combo_start_time >= combo_duration:
                        print("[INFO] L1 + X pressionados por 1s — encerrando o jogo...")
                        process.terminate()
                        break
                else:
                    combo_start_time = None  # Reinicia o contador se soltar

            time.sleep(0.05)

        pygame.quit()

    except Exception as e:
        pygame.quit()
        messagebox.showerror("Erro", f"Falha ao iniciar o jogo:\n{e}")


# ===========================
# 🖼️ CAPAS / ÍCONES
# ===========================


def alterar_capa(nome_jogo, refresh_callback=None):
    """Abre um seletor de imagem e substitui a capa do jogo."""
    try:
        arquivo_img = filedialog.askopenfilename(
            title=f"Selecionar nova capa para {nome_jogo}",
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.webp")],
        )
        if not arquivo_img:
            return

        destino = get_capa_path(f"{nome_jogo}.png")
        Image.open(arquivo_img).convert("RGBA").save(destino, "PNG")

        messagebox.showinfo("Capa atualizada", f"Capa de '{nome_jogo}' alterada com sucesso!")
        if refresh_callback:
            refresh_callback()
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao alterar capa:\n{e}")


def excluir_jogo(nome_jogo, refresh_callback=None):
    """Remove ROM e capa do jogo."""
    try:
        confirmar = messagebox.askyesno(
            "Excluir jogo",
            f"Deseja realmente excluir '{nome_jogo}'?\nA ROM e a capa serão removidas.",
        )
        if not confirmar:
            return

        for ext in (".iso", ".bin", ".img", ".cue", ".chd"):
            rom_path = get_rom_path(f"{nome_jogo}{ext}")
            if os.path.exists(rom_path):
                os.remove(rom_path)

        capa_path = get_capa_path(f"{nome_jogo}.png")
        if os.path.exists(capa_path):
            os.remove(capa_path)

        messagebox.showinfo("Removido", f"O jogo '{nome_jogo}' foi excluído com sucesso.")
        if refresh_callback:
            refresh_callback()
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao excluir jogo:\n{e}")


def encontrar_jogos():
    """Retorna lista de jogos encontrados em /roms com suas capas."""
    os.makedirs(get_rom_path(""), exist_ok=True)
    jogos = []
    for f in os.listdir(get_rom_path("")):
        if f.lower().endswith((".bin", ".iso", ".img", ".cue", ".chd")):
            title = os.path.splitext(f)[0]
            capa_nome = f"{title}.png"
            if not os.path.isfile(get_capa_path(capa_nome)):
                capa_nome = "default.png"
            jogos.append({"title": title, "file": f, "image": capa_nome})
    return jogos


def load_ctk_image(name: str, size=(24, 24)):
    try:
        path = get_icon_path(name)
        img = Image.open(path)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"[WARN] Falha ao carregar ícone {name}: {e}")
        return None


def load_button_image(name: str, size=(24, 24)):
    try:
        path = get_button_path(name)
        img = Image.open(path)
        return CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"[WARN] Falha ao carregar ícone {name}: {e}")
        return None


def load_icons():
    """Carrega todos os ícones padrão da aplicação."""
    return {
        "refresh": load_ctk_image("icon_refresh.png", (32, 32)),
        "search": load_ctk_image("icon_search.png", (32, 32)),
        "edit": load_ctk_image("icon_edit.png", (24, 24)),
        "trash": load_ctk_image("icon_trash.png", (24, 24)),
        "download": load_ctk_image("icon_download.png", (32, 32)),
        "config": load_ctk_image("icon_settings.png", (32, 32)),
        "check": load_ctk_image("icon_check.png", (40, 40)),
        "store": load_ctk_image("icon_store.png", (32, 32)),
        "auto": load_ctk_image("icon_auto.png", (32, 32)),
        "clear": load_ctk_image("icon_clear.png", (32, 32)),
    }
