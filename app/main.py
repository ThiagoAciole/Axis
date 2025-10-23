import os

from ui.home import start_home
from ui.init import start_init
from utils.paths import get_cover_path, get_emulator_path, get_rom_path


def main():
    # === Caminhos base ===
    emulator_dir = get_emulator_path("")
    roms_dir = get_rom_path("")
    covers_dir = get_cover_path("")

    # === Verifica se todas as pastas já existem ===
    if all(os.path.exists(p) for p in (emulator_dir, roms_dir, covers_dir)):
        start_home()
    else:
        start_init()


if __name__ == "__main__":
    main()
