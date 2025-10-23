import os
import shutil
import zipfile

import requests
from utils.constants import *
from utils.theme import *

from .paths import get_cover_path, get_emulator_path, get_rom_path, get_setting_path


def prepare_emulator(progress_callback=None, status_callback=None):
    game_dir = get_emulator_path("")
    rom_dir = get_rom_path("")
    cover_dir = get_cover_path("")

    os.makedirs(game_dir, exist_ok=True)
    os.makedirs(rom_dir, exist_ok=True)
    os.makedirs(cover_dir, exist_ok=True)

    try:
        # === Copiar arquivos padrão ===
        default_src = get_setting_path("default.png")
        default_dest = os.path.join(cover_dir, "default.png")
        if os.path.exists(default_src) and not os.path.exists(default_dest):
            shutil.copy(default_src, default_dest)

        for file in ["games.json", "settings.ini"]:
            src = get_setting_path(file)
            dest = os.path.join(game_dir if file.endswith(".ini") else rom_dir, file)
            if os.path.exists(src) and not os.path.exists(dest):
                shutil.copy(src, dest)

        bios_name = "SCPH1001.BIN"
        bios_dir = os.path.join(game_dir, "bios")
        os.makedirs(bios_dir, exist_ok=True)
        bios_dest = os.path.join(bios_dir, bios_name)
        bios_src = get_setting_path(bios_name)
        if os.path.exists(bios_src) and not os.path.exists(bios_dest):
            shutil.copy(bios_src, bios_dest)

        open(os.path.join(game_dir, "portable.txt"), "a").close()

    except Exception as e:
        print(WARN_COPY_DEFAULT.format(erro=e))

    # === Verifica se o DuckStation já existe ===
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
        status_callback(STATUS_DOWNLOADING)

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
            status_callback(STATUS_EXTRACTING)

        with zipfile.ZipFile(temp_zip, "r") as z:
            z.extractall(path=game_dir)
        os.remove(temp_zip)

    except Exception as e:
        if status_callback:
            status_callback(f"Erro ao baixar DuckStation: {e}")
        return

    if status_callback:
        status_callback(STATUS_READY)
