import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import datetime
from ..config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_ACCENT, COLOR_SECONDARY,
    COLOR_DARK_GRID, COLOR_TEXT_GLOW, COLOR_MUTED, COLOR_TEXT_LIGHT, COLOR_ALERT
)
from ..db import db
from ..api_client import api_client

# ── Display maps ────────────────────────────────────────────────────
PUERTA_MAP = {
    1: "Puerta 1 AV. Té",
    2: "Puerta 2 Resina",
    3: "Puerta 3 Sur 187",
    4: "Puerta 4 Canela"
}
PROG_MAP = {
    1: "Lic. en Administración Industrial",
    2: "Ingeniería en Informática",
    3: "Ingeniería en Transporte",
    4: "Ingeniería Ferroviaria",
    5: "Ingeniería Industrial",
    6: "Lic. en Ciencias de la Informática"
}


class BitacoraFrame(ctk.CTkFrame):
    """
    Muestra los registros de la tabla `acceso` obtenidos desde
    GET /acceso/ en el backend.  Filtros por puerta y texto (nombre/matrícula).
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._api_records = []          # raw data from server
        self._session_records = []      # from current session (db.accesos_db)
        self._api_records_fetched = False
        self._is_fetching = False
        self.setup_ui()

    # ─────────────────────────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────────────────────────

    def setup_ui(self):
        # ── Left Filter Panel ────────────────────────────────────────
        left_panel = ctk.CTkFrame(
            self, fg_color=COLOR_DARK_GRID, width=300,
            corner_radius=0, border_width=1.5, border_color=COLOR_PRIMARY
        )
        left_panel.pack(side="left", fill="y", padx=(0, 15))

        ctk.CTkLabel(
            left_panel, text="> BUSQUEDA_Y_FILTROS",
            font=("Consolas", 14, "bold"), text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=20, pady=20)

        ctk.CTkLabel(left_panel, text="MATRÍCULA / BOLETA:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(10, 2))
        self.search_entry = ctk.CTkEntry(
            left_panel, fg_color="#020204", border_color=COLOR_PRIMARY,
            text_color=COLOR_TEXT_GLOW, font=("Consolas", 13), corner_radius=0
        )
        self.search_entry.pack(fill="x", padx=20, pady=5)
        self.search_entry.bind("<Return>", lambda e: self.filtrar_bitacora())

        ctk.CTkLabel(left_panel, text="PUERTA DE ACCESO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(15, 2))
        self.puerta_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["Todas", "Puerta 1 AV. Té", "Puerta 2 Resina", "Puerta 3 Sur 187", "Puerta 4 Canela"],
            fg_color="#020204", button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF",
            font=("Consolas", 12), corner_radius=0
        )
        self.puerta_menu.pack(fill="x", padx=20, pady=5)
        self.puerta_menu.set("Todas")

        ctk.CTkLabel(left_panel, text="ESTATUS:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", padx=20, pady=(15, 2))
        self.estatus_menu = ctk.CTkOptionMenu(
            left_panel,
            values=["Todos", "Permitido", "Denegado"],
            fg_color="#020204", button_color=COLOR_PRIMARY,
            button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF",
            font=("Consolas", 12), corner_radius=0
        )
        self.estatus_menu.pack(fill="x", padx=20, pady=5)
        self.estatus_menu.set("Todos")

        self.btn_query = tk.Button(
            left_panel, text="FILTRAR BITACORA",
            bg=COLOR_SECONDARY, fg=COLOR_TEXT_LIGHT,
            activebackground=COLOR_TEXT_LIGHT, activeforeground=COLOR_SECONDARY,
            bd=0, relief="flat", highlightthickness=0,
            font=("Consolas", 12, "bold"), command=self.consultar_servidor
        )
        self.btn_query.pack(fill="x", padx=20, pady=15)

        

        # Alert / counter box
        self.alert_box = ctk.CTkFrame(
            left_panel, fg_color="#161408", height=90,
            corner_radius=0, border_width=1.5, border_color=COLOR_ACCENT
        )
        self.alert_box.pack(fill="x", padx=20, pady=(5, 0))
        self.alert_box.pack_propagate(False)
        self.alert_text_lbl = ctk.CTkLabel(
            self.alert_box,
            text="SISTEMA LISTO\nPRESIONA «FILTRAR BITACORA»",
            font=("Courier New", 11, "bold"), text_color=COLOR_ACCENT
        )
        self.alert_text_lbl.pack(expand=True)

        # ── Right Treeview Panel ─────────────────────────────────────
        right_panel = ctk.CTkFrame(
            self, fg_color=COLOR_DARK_GRID,
            corner_radius=0, border_width=1.5, border_color=COLOR_PRIMARY
        )
        right_panel.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            right_panel, text="> BITÁCORA DE ACCESOS EN TIEMPO REAL",
            font=("Consolas", 14, "bold"), text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=20, pady=20)

        # Treeview style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#020204", foreground=COLOR_TEXT_GLOW,
                        rowheight=32, fieldbackground="#020204",
                        bordercolor=COLOR_PRIMARY, borderwidth=1.5, font=("Consolas", 10))
        style.map("Treeview", background=[("selected", "#122416")], foreground=[("selected", COLOR_ACCENT)])
        style.configure("Treeview.Heading", background=COLOR_DARK_GRID, foreground=COLOR_PRIMARY,
                        font=("Consolas", 11, "bold"), borderwidth=1.5, bordercolor=COLOR_PRIMARY)

        tree_frame = tk.Frame(right_panel, bg="#020204")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=15)

        columns = ("fecha", "nombre", "carrera", "puerta", "rol", "movimiento", "estatus")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", style="Treeview")

        heads = {
            "fecha": "FECHA HORA", "nombre": "IDENTIDAD USUARIO",
            "carrera": "PROGRAMA ACADÉMICO", "puerta": "PUERTA ACCESO",
            "rol": "ROL", "movimiento": "MOVIMIENTO", "estatus": "ESTATUS"
        }
        widths = {"fecha": 145, "nombre": 160, "carrera": 240, "puerta": 130, "rol": 80, "movimiento": 65, "estatus": 80}
        anchors = {"nombre": "w", "carrera": "w"}

        for col in columns:
            self.tree.heading(col, text=heads[col])
            self.tree.column(col, width=widths[col], anchor=anchors.get(col, "center"))

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    # ─────────────────────────────────────────────────────────────────
    # DATA FETCH  (from backend API)
    # ─────────────────────────────────────────────────────────────────

    def consultar_servidor(self):
        """Fetch records from GET /acceso/ in background thread."""
        if self._is_fetching:
            return
        self._is_fetching = True
        self.btn_query.config(state="disabled", text="CONSULTANDO...")
        self.alert_text_lbl.configure(text="CONECTANDO CON EL SERVIDOR...", text_color=COLOR_ACCENT)
        threading.Thread(target=self._fetch_thread, daemon=True).start()

    def _fetch_thread(self):
        # Build query params from current filter selection
        puerta_str  = self.puerta_menu.get()
        estatus_str = self.estatus_menu.get()

        puerta_id_param  = None
        estatus_acce_param = None

        if puerta_str != "Todas":
            puerta_map = {"Puerta 1 AV. Té": 1, "Puerta 2 Resina": 2, "Puerta 3 Sur 187": 3, "Puerta 4 Canela": 4}
            puerta_id_param = puerta_map.get(puerta_str)
        if estatus_str == "Permitido":
            estatus_acce_param = 1
        elif estatus_str == "Denegado":
            estatus_acce_param = 0

        success, result = api_client.listar_accesos(
            puerta_id=puerta_id_param,
            estatus_acce=estatus_acce_param,
            limit=300
        )
        self.after(0, lambda: self._on_fetch_done(success, result))

    def _on_fetch_done(self, success, result):
        self._is_fetching = False
        self.btn_query.config(state="normal", text="FILTRAR BITACORA")
        if success:
            self._api_records = result
            self._api_records_fetched = True
            self.alert_text_lbl.configure(
                text=f"SERVIDOR: {len(result)} REGISTRO(S)", text_color=COLOR_PRIMARY
            )
            self.alert_box.configure(border_color=COLOR_PRIMARY)
            self.renderizar_datos_estaticos()
        else:
            self.alert_text_lbl.configure(text=f"ERROR:\n{result}", text_color=COLOR_ALERT)
            self.alert_box.configure(border_color=COLOR_ALERT)

    # ─────────────────────────────────────────────────────────────────
    # RENDER
    # ─────────────────────────────────────────────────────────────────

    def _api_record_to_row(self, rec: dict) -> tuple:
        """Convert an AccesoResponse dict to a treeview row tuple."""
        user = rec.get("usuario") or {}

        fecha_raw = rec.get("fecha_hr", "")
        try:
            fecha = str(fecha_raw)[:19].replace("T", " ")
        except Exception:
            fecha = str(fecha_raw)

        if user:
            nombre  = f"{user.get('nombre','')} {user.get('ap_pat','')}".strip()
            carrera = PROG_MAP.get(user.get("cpa_id"), "—")
            rol     = "Alumnos" if user.get("roles_id") == 2 else "Personal"
        else:
            nombre  = rec.get("motivo") or "INVITADO"
            carrera = "ACCESO POR INVITACIÓN"
            rol     = "Invitados"

        puerta     = PUERTA_MAP.get(rec.get("puerta_id"), f"Puerta {rec.get('puerta_id','?')}")
        tipo_mov   = "ENTRADA" if rec.get("tipo_mov") == 1 else "SALIDA"
        estatus    = "✅ OK" if rec.get("estatus_acce") == 1 else "❌ NEG"

        return (fecha, nombre, carrera, puerta, rol, tipo_mov, estatus)

    def _local_record_to_row(self, rec: dict) -> tuple:
        """Convert a session-local dict (from db.accesos_db) to a treeview row."""
        fecha    = rec.get("fecha", "")
        nombre   = rec.get("nombre", "")
        carrera  = rec.get("carrera", "")
        puerta   = rec.get("puerta", "")
        rol      = rec.get("rol", "")
        estatus  = rec.get("estatus", "")
        tipo_mov = estatus  # stored as ENTRADA/SALIDA already
        ok_lbl   = "✅ OK" if "ENTRADA" in estatus or "SALIDA" in estatus else estatus
        return (fecha, nombre, carrera, puerta, rol, tipo_mov, ok_lbl)

    def renderizar_datos_estaticos(self):
        """
        Called by mainframe on every access event and when view switches.
        Shows current session records (from db) on top of whatever API data we have.
        """
        # If API records haven't been fetched yet, trigger background fetch!
        if not self._api_records_fetched:
            self.consultar_servidor()

        self.tree.delete(*self.tree.get_children())

        # Filter criteria
        search = self.search_entry.get().strip()

        # Render Session-local records first (most recent activity)
        for rec in reversed(db.accesos_db):
            row = self._local_record_to_row(rec)
            rec_matricula = str(rec.get("matricula") or "").strip()
            if not search or (search in rec_matricula):
                self.tree.insert("", "end", values=row)

        # Then Render API records
        if self._api_records:
            for rec in self._api_records:
                row = self._api_record_to_row(rec)
                user_obj = rec.get("usuario") or {}
                rec_matricula = str(user_obj.get("matricula") or "").strip()
                if not search or (search in rec_matricula):
                    self.tree.insert("", "end", values=row)

    # ─────────────────────────────────────────────────────────────────
    # LOCAL FILTER (on already-fetched data)
    # ─────────────────────────────────────────────────────────────────

    def filtrar_bitacora(self):
        """Re-render with current search text applied strictly to matricula field."""
        self.renderizar_datos_estaticos()
        count = len(self.tree.get_children())
        self.alert_text_lbl.configure(
            text=f"FILTRO APLICADO\n{count} RESULTADO(S)",
            text_color=COLOR_PRIMARY
        )
