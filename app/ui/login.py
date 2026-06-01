import customtkinter as ctk
import tkinter as tk
from PIL import Image
from ..config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_ALERT,
    COLOR_TEXT_LIGHT, COLOR_DARK_GRID, COLOR_TEXT_GLOW, COLOR_MUTED,
    CREDENTIALS_DB, get_asset_path
)

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color="transparent")
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        login_card = ctk.CTkFrame(
            self,
            fg_color=COLOR_DARK_GRID,
            width=480,
            height=600,
            corner_radius=10,
            border_width=2,
            border_color=COLOR_PRIMARY
        )
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        login_card.pack_propagate(False)

        logo_header_container = ctk.CTkFrame(login_card, fg_color="transparent", height=120)
        logo_header_container.pack(fill="x", pady=(20, 5))

        ipn_aura_login = ctk.CTkFrame(
            logo_header_container,
            fg_color="#180B11",
            border_width=2,
            border_color=COLOR_ALERT,
            corner_radius=8,
            width=65,
            height=90
        )
        ipn_aura_login.pack(side="left", padx=(50, 10))
        ipn_aura_login.pack_propagate(False)

        try:
            img_ipn_raw = Image.open(get_asset_path("ipn.png"))
            logo_ipn_img = ctk.CTkImage(dark_image=img_ipn_raw, size=(45, 75))
            ctk.CTkLabel(ipn_aura_login, image=logo_ipn_img, text="").pack(expand=True)
        except Exception:
            ctk.CTkLabel(
                ipn_aura_login,
                text="IPN",
                font=("Consolas", 16, "bold"),
                text_color=COLOR_ALERT
            ).pack(expand=True)

        upiicsa_aura_login = ctk.CTkFrame(
            logo_header_container,
            fg_color="#08180E",
            border_width=2,
            border_color=COLOR_PRIMARY,
            corner_radius=8,
            width=75,
            height=90
        )
        upiicsa_aura_login.pack(side="right", padx=(10, 50))
        upiicsa_aura_login.pack_propagate(False)

        try:
            img_upi_raw = Image.open(get_asset_path("upiicsa.png"))
            logo_upi_img = ctk.CTkImage(dark_image=img_upi_raw, size=(55, 75))
            ctk.CTkLabel(upiicsa_aura_login, image=logo_upi_img, text="").pack(expand=True)
        except Exception:
            ctk.CTkLabel(
                upiicsa_aura_login,
                text="UPIICSA",
                font=("Consolas", 14, "bold"),
                text_color=COLOR_PRIMARY
            ).pack(expand=True)

        ctk.CTkLabel(
            login_card,
            text="S A F I P N\nMAINFRAME LOGIN",
            font=("Consolas", 18, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(pady=5)

        self.btn_menu_perfiles = tk.Button(
            login_card,
            text="SELECCIONAR PERFIL DE ACCESO ▾",
            bg=COLOR_DARK_GRID,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY,
            activeforeground="#060709",
            bd=1.5,
            relief="solid",
            font=("Consolas", 11, "bold"),
            command=self.show_profile_menu
        )
        self.btn_menu_perfiles.pack(fill="x", padx=45, pady=(10, 10))

        self.menu_perfiles = tk.Menu(
            self,
            tearoff=0,
            bg=COLOR_DARK_GRID,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY,
            activeforeground="#060709",
            font=("Consolas", 10)
        )
        self.menu_perfiles.add_command(
            label="Administrador Principal",
            command=lambda: self.select_profile("ADMIN_SAFIPN", "1234")
        )
        self.menu_perfiles.add_command(
            label="Desarrollador (Miguel)",
            command=lambda: self.select_profile("MIGUEL_DEV", "MIGUEL2026")
        )
        self.menu_perfiles.add_command(
            label="Diseñador (Christian)",
            command=lambda: self.select_profile("CHRISTIAN_CAMPOS", "DESIGNER_NET")
        )

        ctk.CTkLabel(
            login_card,
            text="USUARIO / MATRÍCULA:",
            font=("Courier New", 11, "bold"),
            text_color=COLOR_MUTED
        ).pack(anchor="w", padx=45, pady=(5, 2))

        self.login_user_entry = ctk.CTkEntry(
            login_card,
            fg_color="#020204",
            border_color=COLOR_PRIMARY,
            text_color=COLOR_TEXT_GLOW,
            font=("Consolas", 13),
            corner_radius=0
        )
        self.login_user_entry.pack(fill="x", padx=45, pady=5)
        self.login_user_entry.insert(0, "ADMIN_SAFIPN")

        ctk.CTkLabel(
            login_card,
            text="CONTRASEÑA DE ACCESO:",
            font=("Courier New", 11, "bold"),
            text_color=COLOR_MUTED
        ).pack(anchor="w", padx=45, pady=(5, 2))

        self.login_pass_entry = ctk.CTkEntry(
            login_card,
            fg_color="#020204",
            border_color=COLOR_PRIMARY,
            text_color=COLOR_TEXT_GLOW,
            font=("Consolas", 13),
            show="*",
            corner_radius=0
        )
        self.login_pass_entry.pack(fill="x", padx=45, pady=5)
        self.login_pass_entry.insert(0, "1234")

        self.login_status_lbl = ctk.CTkLabel(
            login_card,
            text="",
            font=("Consolas", 11),
            text_color="#FFFF00"
        )
        self.login_status_lbl.pack(pady=(5, 0))

        self.btn_login_submit = tk.Button(
            login_card,
            text="AUTENTICAR EN LA RED",
            bg=COLOR_SECONDARY,
            fg=COLOR_TEXT_LIGHT,
            font=("Consolas", 12, "bold"),
            command=self.authenticate_login
        )
        self.btn_login_submit.pack(fill="x", padx=45, pady=(15, 25))

    def show_profile_menu(self):
        x = self.btn_menu_perfiles.winfo_rootx()
        y = self.btn_menu_perfiles.winfo_rooty() + self.btn_menu_perfiles.winfo_height()
        self.menu_perfiles.post(x, y)

    def select_profile(self, username, password):
        self.login_user_entry.delete(0, tk.END)
        self.login_user_entry.insert(0, username)
        self.login_pass_entry.delete(0, tk.END)
        self.login_pass_entry.insert(0, password)
        self.login_status_lbl.configure(text="PERFIL CARGADO CORRECTAMENTE", text_color=COLOR_PRIMARY)

    def authenticate_login(self):
        user = self.login_user_entry.get().strip()
        pwd = self.login_pass_entry.get().strip()
        if user in CREDENTIALS_DB and CREDENTIALS_DB[user]["pass"] == pwd:
            role = CREDENTIALS_DB[user]["role"]
            self.login_status_lbl.configure(
                text="AUTENTICACIÓN EXITOSA // INICIALIZANDO PERFIL...",
                text_color=COLOR_PRIMARY
            )
            self.btn_login_submit.config(state="disabled")
            self.after(1200, lambda: self.on_login_success(user, role))
        else:
            self.login_status_lbl.configure(
                text="ERROR: CREDENCIALES INVÁLIDAS",
                text_color=COLOR_ALERT
            )
