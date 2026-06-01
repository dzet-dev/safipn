import customtkinter as ctk
import tkinter as tk
import time
import datetime
import os
import threading
from ..config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_ACCENT, COLOR_SECONDARY,
    COLOR_ALERT, COLOR_DARK_GRID, COLOR_TEXT_GLOW, COLOR_MUTED, COLOR_TEXT_LIGHT
)
from ..db import db
from ..camera import camera_manager
from ..api_client import api_client
from .captura_biometrica import CapturaBiometrica


class RegistrarFrame(ctk.CTkFrame):
    """
    Panel de registro de acceso biométrico.

    Flujo usuario interno (idéntico a cli.py test_acceso_biometrico):
      1. Selecciona tipo de usuario, movimiento y puerta.
      2. Presiona «PROCESAR ACCESO BIOMÉTRICO».
      3. Se abre ventana OpenCV → usuario presiona ESPACIO.
      4. face_recognition valida el rostro → frame guardado.
      5. POST /acceso/verificar/ → respuesta mostrada en banner.
         La API identifica al usuario por su biometría (sin necesidad de matrícula).

    Flujo visitante:
      POST /acceso/visitante/ sin biometría.
    """

    def __init__(self, parent, on_access_logged):
        super().__init__(parent, fg_color="transparent")
        self.on_access_logged = on_access_logged

        self.cooldown_until = 0
        self.temp_foto_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "temp_acceso.jpg"
        )
        self.camera_image_ref = None
        self._scanning = False

        self.setup_ui()

    # ─────────────────────────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────────────────────────

    def setup_ui(self):
        # ── Left Control Panel ──────────────────────────────────────
        left_control = ctk.CTkFrame(
            self, fg_color=COLOR_DARK_GRID, width=360,
            corner_radius=0, border_width=1.5, border_color=COLOR_PRIMARY
        )
        left_control.pack(side="left", fill="y", padx=(0, 15))
        left_control.pack_propagate(False)

        ctk.CTkLabel(
            left_control, text="> REGISTRO_DE_MOVIMIENTO",
            font=("Consolas", 14, "bold"), text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=20, pady=20)

        # Tipo de usuario
        ctk.CTkLabel(left_control, text="TIPO DE USUARIO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(10, 2))
        self.user_type_menu = ctk.CTkOptionMenu(
            left_control, values=["Interno (Alumno/Profe)", "Invitado"],
            fg_color="#020204", button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF",
            font=("Consolas", 12), corner_radius=0,
            command=self._on_user_type_change
        )
        self.user_type_menu.pack(fill="x", padx=20, pady=5)
        self.user_type_menu.set("Interno (Alumno/Profe)")

        # Tipo de movimiento
        ctk.CTkLabel(left_control, text="TIPO DE MOVIMIENTO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(15, 2))
        self.movement_menu = ctk.CTkOptionMenu(
            left_control, values=["Entrada", "Salida"],
            fg_color="#020204", button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF",
            font=("Consolas", 12), corner_radius=0
        )
        self.movement_menu.pack(fill="x", padx=20, pady=5)
        self.movement_menu.set("Entrada")

        # Puerta
        ctk.CTkLabel(left_control, text="PUERTA DE ACCESO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(15, 2))
        self.reg_puerta_menu = ctk.CTkOptionMenu(
            left_control, values=["Puerta 1 AV. Té", "Puerta 2 Resina", "Puerta 3 Sur 187", "Puerta 4 Canela"],
            fg_color="#020204", button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF",
            font=("Consolas", 12), corner_radius=0
        )
        self.reg_puerta_menu.pack(fill="x", padx=20, pady=5)
        self.reg_puerta_menu.set("Puerta 3 Sur 187")

        # Motivo visitante (oculto por default)
        self.motivo_lbl = ctk.CTkLabel(left_control, text="MOTIVO / NOMBRE DEL VISITANTE:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED)
        self.reg_motivo_entry = ctk.CTkEntry(
            left_control, fg_color="#020204", border_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_GLOW, font=("Consolas", 13), corner_radius=0
        )

        # Instrucción
        self.instruccion_lbl = ctk.CTkLabel(
            left_control,
            text="Presiona el botón y colócate\nfrente a la cámara. Presiona\nESPACIO para capturar tu rostro.",
            font=("Courier New", 10), text_color=COLOR_MUTED, justify="left"
        )
        self.instruccion_lbl.pack(anchor="w", padx=20, pady=(20, 5))

        # Botón principal
        self.btn_execute_reg = tk.Button(
            left_control, text="PROCESAR ACCESO BIOMÉTRICO",
            bg=COLOR_SECONDARY, fg=COLOR_TEXT_LIGHT,
            activebackground=COLOR_TEXT_LIGHT, activeforeground=COLOR_SECONDARY,
            bd=0, relief="flat", highlightthickness=0,
            font=("Consolas", 11, "bold"), command=self.procesar_acceso
        )
        self.btn_execute_reg.pack(fill="x", padx=20, pady=20)

        # ── Right Animation / Status Panel ──────────────────────────
        right_panel = ctk.CTkFrame(
            self, fg_color=COLOR_DARK_GRID,
            corner_radius=0, border_width=1.5, border_color=COLOR_PRIMARY
        )
        right_panel.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            right_panel, text="> CANAL_DE_CAPTURA_FACIAL_BIOMÉTRICA",
            font=("Consolas", 14, "bold"), text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=20, pady=20)

        self.camera_feed_frame = ctk.CTkFrame(
            right_panel, fg_color="#020204",
            border_width=2, border_color=COLOR_ALERT, corner_radius=0
        )
        self.camera_feed_frame.pack(fill="both", expand=True, padx=25, pady=(10, 10))
        self.camera_active_label = ctk.CTkLabel(self.camera_feed_frame, text="", font=("Courier New", 13, "bold"))
        self.camera_active_label.pack(fill="both", expand=True)

        ctk.CTkLabel(
            right_panel,
            text="[ FLUJO: Botón → Ventana cámara → ESPACIO → Verificación → Resultado ]",
            font=("Courier New", 10), text_color=COLOR_MUTED
        ).pack(anchor="w", padx=25, pady=(2, 8))

        # Status banner
        self.camera_status_banner = ctk.CTkFrame(
            right_panel, fg_color="#121418", height=65,
            border_width=1.5, border_color=COLOR_PRIMARY
        )
        self.camera_status_banner.pack(fill="x", padx=25, pady=(0, 25))
        self.camera_status_banner.pack_propagate(False)

        self.camera_status_label = ctk.CTkLabel(
            self.camera_status_banner,
            text="SISTEMA BIOMÉTRICO: EN ESPERA",
            font=("Consolas", 13, "bold"), text_color=COLOR_PRIMARY
        )
        self.camera_status_label.pack(expand=True)

        self._animate_mock_feed()

    # ─────────────────────────────────────────────────────────────────
    # MOCK ANIMATION
    # ─────────────────────────────────────────────────────────────────

    def _animate_mock_feed(self):
        if not self.winfo_exists():
            return
        is_guest = self.user_type_menu.get() == "Invitado"
        pil_img = camera_manager.get_mock_frame(
            is_guest=is_guest, primary_color=COLOR_PRIMARY, accent_color=COLOR_ACCENT
        )
        ctk_img = ctk.CTkImage(dark_image=pil_img, size=(520, 290))
        self.camera_active_label.configure(image=ctk_img, text="")
        self.camera_image_ref = ctk_img
        self.after(40, self._animate_mock_feed)

    # ─────────────────────────────────────────────────────────────────
    # UI HELPERS
    # ─────────────────────────────────────────────────────────────────

    def _on_user_type_change(self, value):
        if value == "Invitado":
            self.instruccion_lbl.configure(text="Presiona el botón para registrar\nel acceso del visitante.\n(No requiere biometría)")
            self.btn_execute_reg.config(text="REGISTRAR ACCESO DE INVITADO")
            self.motivo_lbl.pack(anchor="w", padx=20, pady=(15, 2))
            self.reg_motivo_entry.pack(fill="x", padx=20, pady=5)
        else:
            self.motivo_lbl.pack_forget()
            self.reg_motivo_entry.pack_forget()
            self.instruccion_lbl.configure(text="Presiona el botón y colócate\nfrente a la cámara. Presiona\nESPACIO para capturar tu rostro.")
            self.btn_execute_reg.config(text="PROCESAR ACCESO BIOMÉTRICO")

    def _set_status(self, text, color=None):
        self.camera_status_label.configure(text=text, text_color=color or COLOR_PRIMARY)

    def start_feed(self):
        pass  # Mock animation runs independently

    def stop_feed(self):
        pass

    def _in_cooldown(self) -> bool:
        now = time.time()
        if now < self.cooldown_until:
            remaining = int(self.cooldown_until - now)
            self._set_status(f"COOLDOWN: ESPERE {remaining}s", COLOR_ACCENT)
            return True
        return False

    def _set_cooldown(self, seconds: int):
        self.cooldown_until = time.time() + seconds

    @staticmethod
    def _puerta_id(puerta_str: str) -> int:
        for idx, key in enumerate(["Puerta 1", "Puerta 2", "Puerta 3", "Puerta 4"]):
            if key in puerta_str:
                return idx + 1
        return 3

    # ─────────────────────────────────────────────────────────────────
    # MAIN DISPATCHER
    # ─────────────────────────────────────────────────────────────────

    def procesar_acceso(self):
        if self._in_cooldown() or self._scanning:
            return
        if self.user_type_menu.get() == "Invitado":
            self._procesar_visitante()
        else:
            self._scanning = True
            self.btn_execute_reg.config(state="disabled")
            self._set_status("INICIANDO CÁMARA... ESPERE", COLOR_ACCENT)
            self._abrir_captura_nativa()

    # ─────────────────────────────────────────────────────────────────
    # INTERNO — Captura nativa con CTkToplevel
    # ─────────────────────────────────────────────────────────────────

    def _abrir_captura_nativa(self):
        """Abre la ventana nativa de captura biométrica (sin cv2.imshow)."""
        CapturaBiometrica(
            master=self,
            temp_filename=self.temp_foto_path,
            on_capture=self._on_captura_completada,
            titulo="Acceso Biométrico — SAFIPN",
        )

    def _on_captura_completada(self, foto_path: str | None):
        """
        Callback invocado por CapturaBiometrica al cerrarse.
        Si foto_path es None → captura cancelada o sin rostro.
        Si es un path válido → lanza verificación en thread secundario.
        """
        if not foto_path or not os.path.exists(foto_path):
            self._set_status("CAPTURA CANCELADA O SIN ROSTRO VÁLIDO", COLOR_ALERT)
            self._unlock_button()
            return

        self._set_status("VERIFICANDO CON EL SERVIDOR...", COLOR_ACCENT)
        threading.Thread(
            target=self._verificar_en_servidor,
            args=(foto_path,),
            daemon=True,
        ).start()

    def _verificar_en_servidor(self, foto_path: str):
        """Hilo secundario: envía la foto al backend y procesa la respuesta."""
        try:
            puerta      = self.reg_puerta_menu.get()
            movement    = self.movement_menu.get()
            puerta_id   = self._puerta_id(puerta)
            tipo_mov_id = 1 if movement == "Entrada" else 2

            success, response = api_client.verificar_acceso(puerta_id, tipo_mov_id, foto_path)

            try:
                os.remove(foto_path)
            except Exception:
                pass

            self.after(0, lambda: self._handle_verificar_response(success, response, puerta, movement))

        except Exception as e:
            msg = f"ERROR: {e}"
            self.after(0, lambda: self._set_status(msg, COLOR_ALERT))
        finally:
            self.after(0, self._unlock_button)

    def _handle_verificar_response(self, success, response, puerta, movement):
        if success:
            estatus_acce = response.get("estatus_acce", 0)
            user_info    = response.get("usuario") or {}

            if estatus_acce == 1:
                nombre = f"{user_info.get('nombre','USUARIO')} {user_info.get('ap_pat','')}".strip()
                prog_map = {
                    1: "Lic. en Administración Industrial",
                    2: "Ingeniería en Informática",
                    3: "Ingeniería en Transporte",
                    4: "Ingeniería Ferroviaria",
                    5: "Ingeniería Industrial",
                    6: "Lic. en Ciencias de la Informática"
                }
                carrera = prog_map.get(user_info.get("cpa_id"), "UPIICSA")
                rol     = "Alumnos" if user_info.get("roles_id") == 2 else "Personal"

                db.add_acceso({
                    "fecha":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "nombre":   nombre,
                    "carrera":  carrera,
                    "puerta":   puerta,
                    "rol":      rol,
                    "estatus":  movement.upper(),
                    "matricula": str(user_info.get("matricula", ""))
                })
                msg = (f"✅ ACCESO PERMITIDO — BIENVENIDO, {nombre}"
                       if movement == "Entrada"
                       else f"✅ HASTA PRONTO, {nombre}")
                self._set_status(msg, COLOR_PRIMARY)
            else:
                motivo = response.get("motivo") or "Rostro no reconocido"
                self._set_status(f"❌ ACCESO DENEGADO: {motivo}", COLOR_ALERT)

            self._set_cooldown(7)
        else:
            print(f"[API ERROR] {response}")
            self._set_status(f"❌ ERROR DE CONEXIÓN: {response}", COLOR_ALERT)
            self._set_cooldown(7)

        self.on_access_logged()

    def _unlock_button(self):
        self._scanning = False
        self.btn_execute_reg.config(state="normal")

    # ─────────────────────────────────────────────────────────────────
    # INVITADO
    # ─────────────────────────────────────────────────────────────────

    def _procesar_visitante(self):
        puerta      = self.reg_puerta_menu.get()
        movement    = self.movement_menu.get()
        motivo      = self.reg_motivo_entry.get().strip() or "Acceso por Invitación"
        puerta_id   = self._puerta_id(puerta)
        tipo_mov_id = 1 if movement == "Entrada" else 2

        self._set_status("REGISTRANDO VISITANTE...", COLOR_ACCENT)
        self.update()

        success, response = api_client.registrar_visitante(
            motivo=motivo, puerta_id=puerta_id, tipo_mov=tipo_mov_id
        )

        if success:
            db.add_acceso({
                "fecha":    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nombre":   f"INVITADO — {motivo.upper()}",
                "carrera":  "ACCESO POR INVITACIÓN",
                "puerta":   puerta,
                "rol":      "Invitados",
                "estatus":  movement.upper(),
                "matricula": ""
            })
            self._set_status("✅ ACCESO DE VISITANTE REGISTRADO", COLOR_PRIMARY)
        else:
            self._set_status(f"❌ ERROR: {response}", COLOR_ALERT)

        self._set_cooldown(5)
        self.on_access_logged()
