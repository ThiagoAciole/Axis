import configparser
import os
import threading

import customtkinter as ctk
import pygame
from PIL import Image
from utils.constants import *
from utils.icons import load_button_image, load_icons
from utils.paths import get_asset_path, get_emulator_path
from utils.theme import *


class ControlSettings:
    def __init__(self, parent=None):
        # === Dimensões base ===
        self.base_width = 800
        self.base_height = 600

        # === Janela ===
        self.root = create_window(
            parent=parent,
            title="Configuração de Controle",
            width=self.base_width,
            height=self.base_height,
            resizable=True,
            bg=BACKGROUND_DARK,
        )

        if parent:
            self.root.transient(parent)
            self.root.grab_set()
        self.root.focus_force()
        self.root.lift()

        # === Estado ===
        self.mapping = {}
        self.buttons = {}
        self.settings_path = get_emulator_path("settings.ini")
        self.running = True
        self.active_capture = None
        self.joystick_id = 0
        self.resize_timer = None

        # === Joysticks ===
        pygame.init()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for js in self.joysticks:
            js.init()

        print(f"[DEBUG] Joysticks detectados: {[js.get_name() for js in self.joysticks]}")

        self.load_current_mapping()
        self.build_ui()

        # === Thread de eventos ===
        self.thread = threading.Thread(target=self.listen_joystick_events, daemon=True)
        self.thread.start()

        # === Bind de resize ===
        self.root.bind("<Configure>", self.on_resize)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ==================================
    # 📥 Ler e salvar o [Pad1]
    # ==================================
    def load_current_mapping(self):
        """Lê o arquivo settings.ini ou cria um vazio se não existir."""
        config = configparser.ConfigParser()
        config.optionxform = str  # mantém lowercase

        if not os.path.exists(self.settings_path):
            os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
            empty_pad = {
                "type": "AnalogController",
                "up": "",
                "right": "",
                "down": "",
                "left": "",
                "triangle": "",
                "circle": "",
                "cross": "",
                "square": "",
                "select": "",
                "start": "",
                "l1": "",
                "r1": "",
                "l2": "",
                "r2": "",
                "l3": "",
                "r3": "",
                "lleft": "",
                "lright": "",
                "ldown": "",
                "lup": "",
                "rleft": "",
                "rright": "",
                "rdown": "",
                "rup": "",
            }
            config["Pad1"] = empty_pad
            with open(self.settings_path, "w", encoding="utf-8") as f:
                config.write(f)
            print(f"[INFO] Criado settings.ini vazio em {self.settings_path}")

        config.read(self.settings_path, encoding="utf-8")
        if "Pad1" in config:
            self.mapping = {k.lower(): v for k, v in config["Pad1"].items()}
            print("[DEBUG] Configuração carregada:")
            for k, v in self.mapping.items():
                print(f"  {k} = {v}")

    def save_mapping(self):

        try:
            config = configparser.ConfigParser()
            config.optionxform = str  # mantém lowercase

            # === Lê o arquivo atual (para preservar outras seções) ===
            if os.path.exists(self.settings_path):
                config.read(self.settings_path, encoding="utf-8")

            # === Remove seção antiga [Pad1], se existir ===
            if config.has_section("Pad1"):
                config.remove_section("Pad1")

            # === Verifica se há botões configurados ===
            non_empty = {k.lower(): v for k, v in self.mapping.items() if v.strip()}

            if not non_empty:
                # Nenhum botão configurado → cria só type=None
                config["Pad1"] = {"type": "None"}
                print("[INFO] Nenhum botão configurado. Salvando apenas 'type=None'.")
            else:
                # === Campos padrão obrigatórios ===
                base_pad = {
                    "analog": f"SDL-{self.joystick_id}/Guide",
                    "lleft": f"SDL-{self.joystick_id}/-LeftX",
                    "lright": f"SDL-{self.joystick_id}/+LeftX",
                    "ldown": f"SDL-{self.joystick_id}/+LeftY",
                    "lup": f"SDL-{self.joystick_id}/-LeftY",
                    "rleft": f"SDL-{self.joystick_id}/-RightX",
                    "rright": f"SDL-{self.joystick_id}/+RightX",
                    "rdown": f"SDL-{self.joystick_id}/+RightY",
                    "rup": f"SDL-{self.joystick_id}/-RightY",
                    "type": "AnalogController",
                }

                # === Junta mapeamento do usuário + base obrigatória ===
                config["Pad1"] = {**non_empty, **base_pad}
                print("[INFO] Configuração [Pad1] salva com campos automáticos.")

            # === Escreve o arquivo substituindo apenas [Pad1] ===
            with open(self.settings_path, "w", encoding="utf-8") as f:
                config.write(f)

            # === Log final ===
            for section in config.sections():
                print(f"[{section}]")
                for k, v in config[section].items():
                    print(f"  {k} = {v}")

        except Exception as e:
            print(f"[ERRO] Falha ao salvar configurações: {e}")

    # ==================================
    # 🧱 Interface
    # ==================================
    def build_ui(self):
        w = max(self.root.winfo_width(), self.base_width)
        h = max(self.root.winfo_height(), self.base_height)
        self.px = int(w * 0.025)
        self.py = int(h * 0.02)

        self.header = ctk.CTkFrame(self.root, fg_color=TRANSPARENT)
        self.header.pack(fill="x", pady=(self.py, self.py // 2), padx=self.px)

        icons = load_icons()
        icon_refresh = icons["refresh"]
        icon_auto = icons["auto"]
        icon_clear = icons["clear"]

        pad_names = [f"{js.get_name()}" for i, js in enumerate(self.joysticks)]
        self.device_menu = ctk.CTkOptionMenu(
            self.header,
            values=pad_names or ["Nenhum joystick detectado"],
            width=int(w * 0.75),
            height=36,
            fg_color=SURFACE,
            button_color=PRIMARY_COLOR,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 14),
            command=self.change_joystick,
        )
        self.device_menu.pack(side="left", fill="x", padx=(0, self.px // 2), pady=self.py // 2)

        def create_icon_button(icon, command):
            lbl = ctk.CTkLabel(
                self.header, text="", image=icon, fg_color="transparent", cursor="hand2"
            )
            lbl.pack(side="right", padx=self.px // 3)
            lbl.bind("<Button-1>", lambda e: command())

        create_icon_button(icon_clear, self.reset_buttons)
        create_icon_button(icon_refresh, self.refresh_devices)
        create_icon_button(icon_auto, self.auto_configure)

        self.body = ctk.CTkFrame(self.root, fg_color=BACKGROUND_DARK)
        self.body.pack(fill="both", expand=True, padx=self.px, pady=self.py)

        self.left = ctk.CTkFrame(self.body, fg_color=BACKGROUND_DARK)
        self.left.pack(side="left", fill="y", padx=(self.px, self.px // 2), pady=self.py)

        self.center = ctk.CTkFrame(self.body, fg_color=BACKGROUND_DARK)
        self.center.pack(side="left", expand=True, padx=self.px // 2, pady=self.py)

        self.right = ctk.CTkFrame(self.body, fg_color=BACKGROUND_DARK)
        self.right.pack(side="right", fill="y", padx=(self.px // 2, self.px), pady=self.py)
        rbuttons = (28, 32)
        self.icons = {
            "l1": load_button_image("l1.png", rbuttons),
            "l2": load_button_image("l2.png", rbuttons),
            "r1": load_button_image("r1.png", rbuttons),
            "r2": load_button_image("r2.png", rbuttons),
            "cross": load_button_image("cross.png", (28, 28)),
            "circle": load_button_image("circle.png", (28, 28)),
            "square": load_button_image("square.png", (28, 28)),
            "triangle": load_button_image("triangle.png", (28, 28)),
            "up": load_button_image("up.png", (24, 24)),
            "down": load_button_image("down.png", (24, 24)),
            "left": load_button_image("left.png", (24, 24)),
            "right": load_button_image("right.png", (24, 24)),
            "select": load_button_image("select.png", (24, 24)),
            "start": load_button_image("start.png", (24, 24)),
        }

        self.img_path = get_asset_path("joystick.png")
        self.img_label = None
        self.update_center_image()

        left_buttons = ["l1", "l2", "up", "down", "left", "right", "select"]
        right_buttons = ["r1", "r2", "cross", "square", "circle", "triangle", "start"]

        for name in left_buttons:
            self.create_icon_button(self.left, name)
        for name in right_buttons:
            self.create_icon_button(self.right, name)

        self.footer = ctk.CTkFrame(self.root, fg_color=BACKGROUND)
        self.footer.pack(side="bottom", fill="both")

        button_frame = ctk.CTkFrame(self.footer, fg_color="transparent")
        button_frame.pack(
            side="right",
            pady=(int(self.py * 1.5), int(self.py * 1.5)),
            padx=(self.px, int(self.px * 1.5)),
        )

        ctk.CTkButton(
            button_frame,
            text="Confirmar",
            fg_color=PRIMARY_COLOR,
            hover_color=PRIMARY_HOVER,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 15, FONT_WEIGHT_BOLD),
            corner_radius=10,
            height=40,
            width=120,
            command=self.confirm,
        ).pack(side="right", padx=(self.px // 2, 0))

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            fg_color=SURFACE_LIGHT,
            hover_color=ERROR,
            text_color=TEXT_PRIMARY,
            font=(FONT_FAMILY, 15, FONT_WEIGHT_BOLD),
            corner_radius=10,
            height=40,
            width=120,
            command=self.on_close,
        ).pack(side="right", padx=(self.px // 2, 0))

        self.status_label = ctk.CTkLabel(
            self.footer,
            text="",
            text_color=TEXT_SECONDARY,
            font=(FONT_FAMILY, 13),
            fg_color=BACKGROUND,
        )
        self.status_label.pack(side="left", padx=self.px, pady=(0, self.py // 2))

    # ==================================
    # 🔄 Funções auxiliares
    # ==================================
    def reset_buttons(self):
        for name, btn in self.buttons.items():
            btn.configure(text="Press Button")
        self.mapping = {}
        self.status_label.configure(text="🧹 Todos os botões foram limpos.", text_color=WARNING)
        self.root.after(2500, lambda: self.status_label.configure(text=""))

    def change_joystick(self, value: str):
        try:
            self.joystick_id = int(value.split(":")[0])
            print(f"[INFO] Controle selecionado: SDL-{self.joystick_id}")
        except Exception:
            self.joystick_id = 0

    def create_icon_button(self, parent, name):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=int(self.py * 0.6))

        icon = self.icons.get(name.lower())
        ctk.CTkLabel(frame, image=icon, text="", fg_color="transparent").pack(
            side="left", padx=(0, int(self.px * 0.4))
        )

        value = self.mapping.get(name.lower(), "")
        display = value.split("/", 1)[-1] if "/" in value else value or "Press Button"

        btn = ctk.CTkButton(
            frame,
            text=display,
            fg_color=SURFACE_LIGHT,
            hover_color=PRIMARY_COLOR,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=120,
            height=40,
            font=(FONT_FAMILY, 13, FONT_WEIGHT_BOLD),
            command=lambda n=name.lower(): self.start_capture(n),
        )
        btn.pack(side="left")
        self.buttons[name.lower()] = btn

    # ==================================
    # 🎮 Captura e Pulso visual
    # ==================================
    def listen_joystick_events(self):
        while self.running:
            for event in pygame.event.get():
                if not self.active_capture:
                    if event.type == pygame.JOYBUTTONDOWN:
                        self.highlight_button(event.button)
                    elif event.type == pygame.JOYHATMOTION and event.value != (0, 0):
                        self.highlight_hat(event.value)
                    elif event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.6:
                        self.highlight_axis(event.axis)
                    continue

                btn_name = self.active_capture
                prefix = f"SDL-{self.joystick_id}/"

                if event.type == pygame.JOYHATMOTION and event.value != (0, 0):
                    hat_map = {
                        (0, 1): prefix + "DPadUp",
                        (1, 0): prefix + "DPadRight",
                        (0, -1): prefix + "DPadDown",
                        (-1, 0): prefix + "DPadLeft",
                    }
                    code = hat_map.get(event.value)
                    if code:
                        self.mapping[btn_name] = code
                        self.buttons[btn_name.lower()].configure(text=code)
                        self.active_capture = None

                elif event.type == pygame.JOYBUTTONDOWN:
                    button_map = {
                        0: prefix + "Y",
                        1: prefix + "B",
                        2: prefix + "A",
                        3: prefix + "X",
                        4: prefix + "LeftShoulder",
                        5: prefix + "RightShoulder",
                        6: prefix + "+LeftTrigger",
                        7: prefix + "+RightTrigger",
                        8: prefix + "Back",
                        9: prefix + "Start",
                        10: prefix + "LeftStick",
                        11: prefix + "RightStick",
                    }
                    code = button_map.get(event.button, prefix + f"Button{event.button}")
                    self.mapping[btn_name] = code
                    display_text = code.split("/", 1)[-1] if "/" in code else code
                    self.buttons[btn_name.lower()].configure(text=display_text)
                    print(f"[DEBUG] {btn_name} -> {code}")
                    self.active_capture = None

            pygame.time.wait(10)

    # ==================================
    # ✨ Feedback visual
    # ==================================
    def pulse_icon(self, name):
        btn = self.buttons.get(name)
        if not btn:
            return
        original_color = btn.cget("fg_color")

        def animate(step=0):
            if step == 0:
                btn.configure(fg_color=PRIMARY_COLOR)
                self.root.after(120, lambda: animate(1))
            elif step == 1:
                btn.configure(fg_color=original_color)

        animate()

    def highlight_button(self, button_id):
        map_id = {
            0: "triangle",
            1: "circle",
            2: "cross",
            3: "square",
            4: "l1",
            5: "r1",
            6: "l2",
            7: "r2",
            8: "select",
            9: "start",
            10: "l3",
            11: "r3",
        }
        name = map_id.get(button_id)
        if name:
            self.pulse_icon(name)
            print(f"[PULSE] {name.upper()} pressionado (Joy {button_id})")

    def highlight_hat(self, direction):
        x, y = direction
        if y == 1:
            self.pulse_icon("up")
        elif y == -1:
            self.pulse_icon("down")
        elif x == 1:
            self.pulse_icon("right")
        elif x == -1:
            self.pulse_icon("left")

    def highlight_axis(self, axis):
        if axis in (0, 1):
            side = "l"
        elif axis in (2, 3):
            side = "r"
        else:
            return
        print(f"[PULSE] Movimento analógico {side.upper()} detectado.")
        self.pulse_icon(f"{side}up")

    # ==================================
    # 💾 Confirmação e Encerramento
    # ==================================
    def start_capture(self, name):
        for btn in self.buttons.values():
            btn.configure(fg_color=SURFACE_LIGHT)
        self.active_capture = name
        self.buttons[name.lower()].configure(fg_color=PRIMARY_HOVER, text="Aguardando...")

    def confirm(self):
        self.running = False
        self.save_mapping()

        # Feedback no footer
        self.status_label.configure(text="✅ Configuração salva com sucesso!", text_color=SUCCESS)

        def fade_out(step=0):
            if step == 0:
                self.root.after(3000, lambda: fade_out(1))
            elif step == 1:
                self.status_label.configure(text="")

        fade_out()

    def on_close(self):
        self.running = False
        pygame.quit()
        self.root.destroy()

    def refresh_devices(self):
        """Atualiza a lista de controles conectados."""
        pygame.joystick.quit()
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for js in self.joysticks:
            js.init()

        pad_names = [f"{i}: {js.get_name()}" for i, js in enumerate(self.joysticks)]
        self.device_menu.configure(values=pad_names or ["Nenhum joystick detectado"])
        self.status_label.configure(
            text="🔄 Lista de controles atualizada.", text_color=PRIMARY_HOVER
        )
        self.root.after(2500, lambda: self.status_label.configure(text=""))

    def auto_configure(self):
        if not self.joysticks:
            self.status_label.configure(text="⚠️ Nenhum controle detectado.", text_color=WARNING)
            return

        try:
            js = self.joysticks[self.joystick_id]
            prefix = f"SDL-{self.joystick_id}/"
            self.mapping = {
                "up": prefix + "DPadUp",
                "right": prefix + "DPadRight",
                "down": prefix + "DPadDown",
                "left": prefix + "DPadLeft",
                "triangle": prefix + "Y",
                "circle": prefix + "B",
                "cross": prefix + "A",
                "square": prefix + "X",
                "select": prefix + "Back",
                "start": prefix + "Start",
                "l1": prefix + "LeftShoulder",
                "r1": prefix + "RightShoulder",
                "l2": prefix + "+LeftTrigger",
                "r2": prefix + "+RightTrigger",
                "l3": prefix + "LeftStick",
                "r3": prefix + "RightStick",
            }
            for name, btn in self.buttons.items():
                if name in self.mapping:
                    btn.configure(text=self.mapping[name].split("/")[-1])
            self.status_label.configure(
                text=f"⚙️ Controle '{js.get_name()}' configurado automaticamente.",
                text_color=SUCCESS,
            )
            self.root.after(2500, lambda: self.status_label.configure(text=""))
        except Exception as e:
            print(f"[ERRO] Falha ao configurar controle automaticamente: {e}")
            self.status_label.configure(text="❌ Erro ao configurar controle.", text_color=ERROR)

    # ==================================
    # 🔁 Resize dinâmico
    # ==================================
    def on_resize(self, event):
        # Debounce para evitar recalcular em excesso
        if self.resize_timer:
            self.root.after_cancel(self.resize_timer)
        self.resize_timer = self.root.after(100, self.update_layout)

    def update_layout(self):
        w = max(self.root.winfo_width(), 600)
        h = max(self.root.winfo_height(), 420)

        # paddings proporcionais
        self.px = int(w * 0.025)
        self.py = int(h * 0.02)

        # atualiza header/body/footer paddings
        self.header.pack_configure(padx=self.px, pady=(self.py, self.py // 2))
        self.body.pack_configure(padx=self.px, pady=self.py)
        self.footer.pack_configure(pady=(self.py, self.py // 12))

        # width do optionmenu acompanha
        self.device_menu.configure(width=int(w * 0.55))

        # Reposiciona frames laterais (a proporção visual é mantida pelos paddings)
        for child in (self.left, self.center, self.right):
            child.pack_configure(padx=self.px // 2, pady=self.py)

        # Atualiza imagem central proporcional
        self.update_center_image(w, h)

        # Atualiza espaçamentos das linhas de botões
        # (reaplica pack dos frames dos botões)
        for frame in self.left.winfo_children() + self.right.winfo_children():
            frame.pack_configure(pady=int(self.py * 0.6))

    def update_center_image(self, w=None, h=None):
        if not os.path.exists(self.img_path):
            return
        if w is None:
            w = max(self.root.winfo_width(), self.base_width)
        if h is None:
            h = max(self.root.winfo_height(), self.base_height)

        img_w = int(w * 0.45)
        img_h = int(h * 0.35)

        img = ctk.CTkImage(Image.open(self.img_path), size=(img_w, img_h))
        if self.img_label:
            self.img_label.configure(image=img)
            self.img_label.image = img
        else:
            self.img_label = ctk.CTkLabel(self.center, text="", image=img)
            self.img_label.pack(pady=int(h * 0.05))
            self.img_label.image = img  # evita GC
