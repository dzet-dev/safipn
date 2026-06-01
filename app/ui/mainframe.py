import customtkinter as ctk
import tkinter as tk
import threading
from PIL import Image
from ..config import (
    COLOR_BG, COLOR_PRIMARY, COLOR_ACCENT, COLOR_ALERT,
    COLOR_DARK_GRID, COLOR_TEXT_GLOW, COLOR_MUTED, get_asset_path
)
from ..api_client import api_client
from .login import LoginFrame
from .bitacora import BitacoraFrame
from .registrar import RegistrarFrame
from .gestionar import GestionarFrame

class SAFIPNMainframeInterface(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("SAFIPN")
        self.geometry("1280x750")
        self.configure(fg_color=COLOR_BG)

        self.current_user = None
        self.current_role = None

        self.setup_ui_containers()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui_containers(self):
        # 1. Login view container
        self.login_view = LoginFrame(self, on_login_success=self.complete_login_transition)
        self.login_view.pack(fill="both", expand=True)

        # 2. Main app view container (hidden initially)
        self.main_app_view = ctk.CTkFrame(self, fg_color="transparent")

    def complete_login_transition(self, username, role):
        self.current_user = username
        self.current_role = role

        # Transition screens
        self.login_view.pack_forget()
        self.main_app_view.pack(fill="both", expand=True)

        # Build main layout
        self.setup_mainframe_layout()
        
        # Apply role permissions
        self.apply_role_permissions()

        # Async API health check to update the status badge
        threading.Thread(target=self._check_api_health, daemon=True).start()

    def setup_mainframe_layout(self):
        # Header
        header_frame = ctk.CTkFrame(
            self.main_app_view,
            fg_color=COLOR_DARK_GRID,
            height=110,
            corner_radius=0,
            border_width=2,
            border_color=COLOR_PRIMARY
        )
        header_frame.pack(fill="x", padx=15, pady=15)
        header_frame.pack_propagate(False)

        # IPN Logo
        ipn_aura = ctk.CTkFrame(
            header_frame,
            fg_color="#180B11",
            border_width=2,
            border_color=COLOR_ALERT,
            corner_radius=8,
            width=65,
            height=90
        )
        ipn_aura.pack(side="left", padx=15, pady=10)
        ipn_aura.pack_propagate(False)

        try:
            img_ipn_raw = Image.open(get_asset_path("ipn.png"))
            logo_ipn_img = ctk.CTkImage(dark_image=img_ipn_raw, size=(45, 75))
            ctk.CTkLabel(ipn_aura, image=logo_ipn_img, text="").pack(expand=True)
        except Exception:
            ctk.CTkLabel(ipn_aura, text="IPN", font=("Consolas", 16, "bold"), text_color=COLOR_ALERT).pack(expand=True)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="S I S T E M A  D E  C O N T R O L  D E  A C C E S O  -  S A F I P N",
            font=("Consolas", 20, "bold"),
            text_color=COLOR_PRIMARY
        )
        title_label.pack(side="left", padx=20, expand=True)

        # UPIICSA Logo
        upiicsa_aura = ctk.CTkFrame(
            header_frame,
            fg_color="#08180E",
            border_width=2,
            border_color=COLOR_PRIMARY,
            corner_radius=8,
            width=75,
            height=90
        )
        upiicsa_aura.pack(side="right", padx=15, pady=10)
        upiicsa_aura.pack_propagate(False)

        try:
            img_upi_raw = Image.open(get_asset_path("upiicsa.png"))
            logo_upi_img = ctk.CTkImage(dark_image=img_upi_raw, size=(55, 75))
            ctk.CTkLabel(upiicsa_aura, image=logo_upi_img, text="").pack(expand=True)
        except Exception:
            ctk.CTkLabel(upiicsa_aura, text="UPIICSA", font=("Consolas", 14, "bold"), text_color=COLOR_PRIMARY).pack(expand=True)

        # Status Badge
        status_container = ctk.CTkFrame(
            header_frame,
            fg_color="transparent",
            border_width=1.5,
            border_color=COLOR_ACCENT,
            corner_radius=0
        )
        status_container.pack(side="right", padx=10, pady=15)

        self.status_signal = ctk.CTkLabel(
            status_container,
            text="ESTADO: INICIALIZANDO",
            font=("Courier New", 12, "bold"),
            text_color=COLOR_ACCENT,
            padx=15,
            pady=6
        )
        self.status_signal.pack()

        # Main Workspace Container
        workspace = ctk.CTkFrame(self.main_app_view, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=15, pady=5)

        # Sidebar Panel (Navigation)
        self.nav_panel = ctk.CTkFrame(
            workspace,
            fg_color=COLOR_DARK_GRID,
            width=220,
            corner_radius=0,
            border_width=1.5,
            border_color=COLOR_PRIMARY
        )
        self.nav_panel.pack(side="left", fill="y", padx=(0, 15))
        self.nav_panel.pack_propagate(False)

        ctk.CTkLabel(
            self.nav_panel,
            text="> MENÚ PRINCIPAL",
            font=("Consolas", 14, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=15, pady=20)

        self.btn_nav_bitacora = tk.Button(
            self.nav_panel,
            text="BITÁCORA ACCESOS",
            bg=COLOR_DARK_GRID,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY,
            activeforeground="#020204",
            bd=1.5,
            relief="solid",
            font=("Consolas", 11, "bold"),
            command=lambda: self.show_view("bitacora")
        )
        self.btn_nav_bitacora.pack(fill="x", padx=15, pady=10)

        self.btn_nav_registrar = tk.Button(
            self.nav_panel,
            text="REGISTRAR ACCESO",
            bg=COLOR_DARK_GRID,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY,
            activeforeground="#020204",
            bd=1.5,
            relief="solid",
            font=("Consolas", 11, "bold"),
            command=lambda: self.show_view("registrar")
        )
        self.btn_nav_registrar.pack(fill="x", padx=15, pady=10)

        self.btn_nav_agregar = tk.Button(
            self.nav_panel,
            text="GESTIONAR USUARIOS",
            bg=COLOR_DARK_GRID,
            fg=COLOR_PRIMARY,
            activebackground=COLOR_PRIMARY,
            activeforeground="#020204",
            bd=1.5,
            relief="solid",
            font=("Consolas", 11, "bold"),
            command=lambda: self.show_view("agregar")
        )
        self.btn_nav_agregar.pack(fill="x", padx=15, pady=10)

        # Right Content Container
        self.content_container = ctk.CTkFrame(workspace, fg_color="transparent")
        self.content_container.pack(side="right", fill="both", expand=True)

        # Lazy load UI views to avoid initialization side-effects
        self.view_bitacora = BitacoraFrame(self.content_container)
        self.view_registrar = RegistrarFrame(self.content_container, on_access_logged=self.refresh_bitacora_data)
        self.view_agregar = GestionarFrame(self.content_container)

    def apply_role_permissions(self):
        if self.current_role == "Administrador":
            self.status_signal.configure(text="ROL: ADMINISTRADOR", text_color=COLOR_PRIMARY)
            self.show_view("bitacora")
        elif self.current_role == "Desarrollador":
            self.status_signal.configure(text="ROL: DESARROLLADOR", text_color=COLOR_ACCENT)
            self.btn_nav_agregar.config(state="disabled")
            self.show_view("bitacora")
        elif self.current_role == "Diseñador":
            self.status_signal.configure(text="ROL: SOLO LECTURA", text_color=COLOR_ALERT)
            self.btn_nav_registrar.config(state="disabled")
            self.btn_nav_agregar.config(state="disabled")
            self.show_view("bitacora")

    def show_view(self, view_name):
        # Stop webcam feed if shifting away from scan panel
        if view_name != "registrar":
            self.view_registrar.stop_feed()

        # Hide all views
        self.view_bitacora.pack_forget()
        self.view_registrar.pack_forget()
        self.view_agregar.pack_forget()

        # Deselect all buttons
        self.btn_nav_bitacora.config(bg=COLOR_DARK_GRID, fg=COLOR_PRIMARY)
        self.btn_nav_registrar.config(bg=COLOR_DARK_GRID, fg=COLOR_PRIMARY)
        self.btn_nav_agregar.config(bg=COLOR_DARK_GRID, fg=COLOR_PRIMARY)

        # Activate selected view and colorize its button
        if view_name == "bitacora":
            self.view_bitacora.pack(fill="both", expand=True)
            self.btn_nav_bitacora.config(bg=COLOR_PRIMARY, fg="#020204")
            self.view_bitacora.renderizar_datos_estaticos()
        elif view_name == "registrar":
            self.view_registrar.pack(fill="both", expand=True)
            self.btn_nav_registrar.config(bg=COLOR_PRIMARY, fg="#020204")
            self.view_registrar.start_feed()
        elif view_name == "agregar":
            self.view_agregar.pack(fill="both", expand=True)
            self.btn_nav_agregar.config(bg=COLOR_PRIMARY, fg="#020204")

    def refresh_bitacora_data(self):
        """Forces refreshing the logs Treeview."""
        if hasattr(self, 'view_bitacora') and self.view_bitacora.winfo_exists():
            self.view_bitacora.renderizar_datos_estaticos()

    def _check_api_health(self):
        """Runs in background thread: pings /  and updates the status badge."""
        is_online = api_client.check_health()
        if is_online:
            self.after(0, lambda: self.status_signal.configure(
                text="API SAFIPN: EN LÍNEA  ●",
                text_color=COLOR_PRIMARY
            ))
        else:
            self.after(0, lambda: self.status_signal.configure(
                text="API SAFIPN: FUERA DE LÍNEA  ●",
                text_color=COLOR_ALERT
            ))

    def on_closing(self):
        # Stop camera first if active
        if hasattr(self, 'view_registrar'):
            self.view_registrar.stop_feed()
        self.destroy()
