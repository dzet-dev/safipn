import customtkinter as ctk
import tkinter as tk
import os
from ..config import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_ACCENT, COLOR_SECONDARY,
    COLOR_ALERT, COLOR_DARK_GRID, COLOR_TEXT_GLOW, COLOR_MUTED, COLOR_TEXT_LIGHT
)
from ..db import db
from ..camera import camera_manager
from ..api_client import api_client

class GestionarFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.current_updating_id = None
        self.setup_ui()

    def setup_ui(self):
        self.tab_control = ctk.CTkTabview(
            self,
            segmented_button_selected_color=COLOR_PRIMARY,
            segmented_button_selected_hover_color=COLOR_PRIMARY_HOVER,
            segmented_button_unselected_color=COLOR_DARK_GRID,
            text_color="#FFFFFF"
        )
        self.tab_control.pack(fill="both", expand=True)

        self.tab_alta = self.tab_control.add("ALTA DE IDENTIDADES")
        self.tab_update = self.tab_control.add("ACTUALIZACIÓN DE IDENTIDADES")

        self.build_alta_form()
        self.build_update_form()

    def build_alta_form(self):
        form_panel = ctk.CTkFrame(
            self.tab_alta,
            fg_color=COLOR_DARK_GRID,
            corner_radius=0,
            border_width=1.5,
            border_color=COLOR_PRIMARY
        )
        form_panel.pack(fill="both", expand=True)

        ctk.CTkLabel(
            form_panel,
            text="> ALTA_DE_IDENTIDAD_EN_SISTEMA_SAFIPN",
            font=("Consolas", 14, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=20, pady=15)

        fields_container = ctk.CTkFrame(form_panel, fg_color="transparent")
        fields_container.pack(fill="both", expand=True, padx=20)

        left_column = ctk.CTkFrame(fields_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(fields_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Left Column Fields
        ctk.CTkLabel(left_column, text="MATRÍCULA / BOLETA:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_add_matricula = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_add_matricula.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="NOMBRE(S):", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_add_nombre = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_add_nombre.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="APELLIDO PATERNO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_add_pat = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_add_pat.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="APELLIDO MATERNO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_add_mat = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_add_mat.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="CURP:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_add_curp = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_add_curp.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="FECHA NACIMIENTO (AAAA-MM-DD):", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_add_fech_naci = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_add_fech_naci.pack(fill="x", pady=(0, 5))
        self.entry_add_fech_naci.insert(0, "2000-01-01")

        # Right Column Fields
        ctk.CTkLabel(right_column, text="SEXO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_add_sex = ctk.CTkOptionMenu(right_column, values=["M (Masculino)", "F (Femenino)"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_add_sex.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="TURNO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_add_turno = ctk.CTkOptionMenu(right_column, values=["M (Matutino)", "V (Vespertino)", "X (Mixto)"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_add_turno.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="ROL EN INSTITUCIÓN:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_add_rol = ctk.CTkOptionMenu(right_column, values=["Personal", "Alumnos"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_add_rol.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="PROGRAMA ACADÉMICO / UNIDAD:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_add_prog = ctk.CTkOptionMenu(right_column, values=["Licenciatura en Administración Industrial", "Ingeniería en Informática", "Ingeniería en Transporte", "Ingeniería Ferroviaria", "Ingeniería Industrial", "Licenciatura en Ciencias de la Informática"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_add_prog.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="VIGENCIA:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_add_vigencia = ctk.CTkOptionMenu(right_column, values=["Activo", "Inactivo"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_add_vigencia.pack(fill="x", pady=(0, 5))

        self.add_user_status_lbl = ctk.CTkLabel(form_panel, text="", font=("Consolas", 12, "bold"), text_color=COLOR_PRIMARY)
        self.add_user_status_lbl.pack(pady=2)

        self.btn_save_user = tk.Button(
            form_panel,
            text="REGISTRAR IDENTIDAD Y CAPTURAR ROSTRO",
            bg=COLOR_SECONDARY,
            fg=COLOR_TEXT_LIGHT,
            activebackground=COLOR_TEXT_LIGHT,
            activeforeground=COLOR_SECONDARY,
            bd=0,
            relief="flat",
            highlightthickness=0,
            font=("Consolas", 12, "bold"),
            command=self.alta_usuario_biometrico
        )
        self.btn_save_user.pack(fill="x", padx=20, pady=(2, 10))

    def build_update_form(self):
        update_panel = ctk.CTkFrame(
            self.tab_update,
            fg_color=COLOR_DARK_GRID,
            corner_radius=0,
            border_width=1.5,
            border_color=COLOR_ACCENT
        )
        update_panel.pack(fill="both", expand=True)

        ctk.CTkLabel(
            update_panel,
            text="> ACTUALIZACIÓN / MODIFICACIÓN DE EXPEDIENTES",
            font=("Consolas", 14, "bold"),
            text_color=COLOR_ACCENT
        ).pack(anchor="w", padx=20, pady=15)

        search_sec = ctk.CTkFrame(update_panel, fg_color="transparent")
        search_sec.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            search_sec,
            text="MATRÍCULA A CONSULTAR:",
            font=("Courier New", 11, "bold"),
            text_color=COLOR_ACCENT
        ).pack(side="left", padx=(0, 10))

        self.entry_update_search = ctk.CTkEntry(
            search_sec,
            fg_color="#020204",
            border_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_GLOW,
            font=("Consolas", 12),
            corner_radius=0,
            width=200
        )
        self.entry_update_search.pack(side="left", padx=(0, 15))
        self.entry_update_search.insert(0, "2020601647")

        self.btn_load_user_data = tk.Button(
            search_sec,
            text="CARGAR EXPEDIENTE",
            bg=COLOR_DARK_GRID,
            fg=COLOR_ACCENT,
            activebackground=COLOR_ACCENT,
            activeforeground="#020204",
            bd=1.5,
            relief="solid",
            highlightthickness=0,
            font=("Consolas", 11, "bold"),
            command=self.load_user_fields_for_updating
        )
        self.btn_load_user_data.pack(side="left")

        fields_container = ctk.CTkFrame(update_panel, fg_color="transparent")
        fields_container.pack(fill="both", expand=True, padx=20)

        left_column = ctk.CTkFrame(fields_container, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(fields_container, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Left Column Fields (Upd)
        ctk.CTkLabel(left_column, text="NOMBRE(S):", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_upd_nombre = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_upd_nombre.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="APELLIDO PATERNO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_upd_pat = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_upd_pat.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="APELLIDO MATERNO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_upd_mat = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_upd_mat.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="CURP:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_upd_curp = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_upd_curp.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(left_column, text="FECHA NACIMIENTO (AAAA-MM-DD):", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.entry_upd_fech_naci = ctk.CTkEntry(left_column, fg_color="#020204", border_color=COLOR_PRIMARY, text_color=COLOR_TEXT_GLOW, font=("Consolas", 12), corner_radius=0)
        self.entry_upd_fech_naci.pack(fill="x", pady=(0, 5))

        # Right Column Menus (Upd)
        ctk.CTkLabel(right_column, text="SEXO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_upd_sex = ctk.CTkOptionMenu(right_column, values=["M (Masculino)", "F (Femenino)"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_upd_sex.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="TURNO:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_upd_turno = ctk.CTkOptionMenu(right_column, values=["M (Matutino)", "V (Vespertino)", "X (Mixto)"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_upd_turno.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="ROL EN INSTITUCIÓN:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_upd_rol = ctk.CTkOptionMenu(right_column, values=["Personal", "Alumnos"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_upd_rol.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="PROGRAMA ACADÉMICO / UNIDAD:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_upd_prog = ctk.CTkOptionMenu(right_column, values=["Licenciatura en Administración Industrial", "Ingeniería en Informática", "Ingeniería en Transporte", "Ingeniería Ferroviaria", "Ingeniería Industrial", "Licenciatura en Ciencias de la Informática"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_upd_prog.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(right_column, text="VIGENCIA:", font=("Courier New", 11, "bold"), text_color=COLOR_MUTED).pack(anchor="w", pady=(2, 1))
        self.menu_upd_vigencia = ctk.CTkOptionMenu(right_column, values=["Activo", "Inactivo"], fg_color="#020204", button_color=COLOR_PRIMARY, button_hover_color=COLOR_PRIMARY_HOVER, text_color="#FFFFFF", font=("Consolas", 12), dropdown_font=("Consolas", 12), dropdown_fg_color=COLOR_DARK_GRID, corner_radius=0)
        self.menu_upd_vigencia.pack(fill="x", pady=(0, 5))

        self.upd_user_status_lbl = ctk.CTkLabel(update_panel, text="", font=("Consolas", 12, "bold"), text_color=COLOR_ACCENT)
        self.upd_user_status_lbl.pack(pady=2)

        self.btn_update_user = tk.Button(
            update_panel,
            text="ACTUALIZAR EXPEDIENTE EN LA RED",
            bg=COLOR_SECONDARY,
            fg=COLOR_TEXT_LIGHT,
            activebackground=COLOR_TEXT_LIGHT,
            activeforeground=COLOR_SECONDARY,
            bd=0,
            relief="flat",
            highlightthickness=0,
            font=("Consolas", 12, "bold"),
            command=self.execute_user_record_update
        )
        self.btn_update_user.pack(fill="x", padx=20, pady=(2, 5))

        self.btn_delete_user = tk.Button(
            update_panel,
            text="ELIMINAR USUARIO DE LA RED",
            bg=COLOR_ALERT,
            fg=COLOR_TEXT_LIGHT,
            activebackground=COLOR_TEXT_LIGHT,
            activeforeground=COLOR_ALERT,
            bd=0,
            relief="flat",
            highlightthickness=0,
            font=("Consolas", 12, "bold"),
            command=self.execute_user_record_delete
        )
        self.btn_delete_user.pack(fill="x", padx=20, pady=(5, 10))

    def map_cpa_id(self, desc):
        mapping = {
            "Licenciatura en Administración Industrial": 1,
            "Ingeniería en Informática": 2,
            "Ingeniería en Transporte": 3,
            "Ingeniería Ferroviaria": 4,
            "Ingeniería Industrial": 5,
            "Licenciatura en Ciencias de la Informática": 6
        }
        return mapping.get(desc, 1)

    def map_role_id(self, desc):
        mapping = {
            "Personal": 1,
            "Alumnos": 2
        }
        return mapping.get(desc, 2)

    def alta_usuario_biometrico(self):
        mat = self.entry_add_matricula.get().strip()
        nom = self.entry_add_nombre.get().strip()
        pat = self.entry_add_pat.get().strip()
        fech_naci = self.entry_add_fech_naci.get().strip()
        curp = self.entry_add_curp.get().strip()

        if mat == "" or nom == "" or pat == "" or fech_naci == "" or curp == "":
            self.add_user_status_lbl.configure(text="ERROR: TODOS LOS CAMPOS SON REQUERIDOS (EXCEPTO AP. MATERNO)", text_color=COLOR_ALERT)
            return

        # Prepare user data
        roles_id = self.map_role_id(self.menu_add_rol.get())
        cpa_id = self.map_cpa_id(self.menu_add_prog.get())
        vigencia = 1 if self.menu_add_vigencia.get() == "Activo" else 0
        sexo = "M" if "Masculino" in self.menu_add_sex.get() else "F"
        turno = self.menu_add_turno.get()[0] # get M, V or X

        usuario_payload = {
            "nombre": nom.upper(),
            "ap_pat": pat.upper(),
            "ap_mat": self.entry_add_mat.get().strip().upper() or None,
            "fech_naci": fech_naci,
            "curp": curp.upper(),
            "sexo": sexo,
            "turno": turno,
            "vigencia": vigencia,
            "roles_id": roles_id,
            "cpa_id": cpa_id,
            "matricula": int(mat) if mat.isdigit() else None
        }

        # Check API health
        is_online = api_client.check_health()
        if is_online:
            self.add_user_status_lbl.configure(text="INICIALIZANDO CÁMARA PARA CAPTURA DE ROSTRO...", text_color=COLOR_ACCENT)
            self.update()
            
            # Snap photo
            temp_path = "temp_registro.jpg"
            foto_path = camera_manager.capture_face_with_popup(title="Registro Biometrico SAFIPN", temp_filename=temp_path, mensaje_instruccion="Acomodate y presiona ESPACIO. (q para salir)")
            
            if foto_path and os.path.exists(foto_path):
                self.add_user_status_lbl.configure(text="TRANSMITIENDO EXPEDIENTE BIOMÉTRICO...", text_color=COLOR_ACCENT)
                self.update()
                
                success, response = api_client.registrar_usuario(usuario_payload, foto_path)
                
                # Cleanup photo
                try:
                    os.remove(foto_path)
                except:
                    pass
                
                if success:
                    self.add_user_status_lbl.configure(
                        text=f"ÉXITO: '{nom.upper()}' REGISTRADO EN SERVIDOR Y RED BIOMÉTRICA",
                        text_color=COLOR_PRIMARY
                    )
                    self.clear_alta_fields()
                else:
                    self.add_user_status_lbl.configure(text=f"FALLO SERVIDOR: {response}", text_color=COLOR_ALERT)
            else:
                self.add_user_status_lbl.configure(text="CAPTURA BIOMÉTRICA CANCELADA O SIN ROSTRO DETECTADO", text_color=COLOR_ALERT)
        else:
            self.add_user_status_lbl.configure(
                text="ERROR: SERVIDOR FUERA DE LÍNEA. NO SE PUEDE COMPLETAR EL REGISTRO.",
                text_color=COLOR_ALERT
            )

    def clear_alta_fields(self):
        for entry in [self.entry_add_matricula, self.entry_add_nombre, self.entry_add_pat, self.entry_add_mat, self.entry_add_curp, self.entry_add_fech_naci]:
            entry.delete(0, tk.END)
        self.entry_add_fech_naci.insert(0, "2000-01-01")

    def load_user_fields_for_updating(self):
        target = self.entry_update_search.get().strip()
        self.current_updating_id = None

        is_online = api_client.check_health()
        user_data = None
        
        if is_online:
            success, list_res = api_client.listar_usuarios()
            if success:
                # search by matricula
                for usr in list_res:
                    if str(usr.get("matricula")) == target:
                        user_data = usr
                        self.current_updating_id = usr.get("id_usuario")
                        break
            else:
                self.upd_user_status_lbl.configure(text=f"ERROR SERVIDOR: {list_res}", text_color=COLOR_ALERT)
                return
        else:
            self.upd_user_status_lbl.configure(text="ERROR: SERVIDOR FUERA DE LÍNEA", text_color=COLOR_ALERT)
            return

        if user_data:
            # Populate UI inputs
            for entry, val in [
                (self.entry_upd_nombre, 'nombre'),
                (self.entry_upd_pat, 'ap_pat'),
                (self.entry_upd_mat, 'ap_mat'),
                (self.entry_upd_curp, 'curp'),
                (self.entry_upd_fech_naci, 'fech_naci')
            ]:
                entry.delete(0, tk.END)
                entry.insert(0, user_data.get(val, "") or "")
                
            self.menu_upd_sex.set("M (Masculino)" if user_data.get("sexo") == "M" else "F (Femenino)")
            
            turno_map = {"M": "M (Matutino)", "V": "V (Vespertino)", "X": "X (Mixto)"}
            self.menu_upd_turno.set(turno_map.get(user_data.get("turno"), "M (Matutino)"))
            
            self.menu_upd_rol.set("Personal" if user_data.get("roles_id") == 1 else "Alumnos")
            
            prog_map = {
                1: "Licenciatura en Administración Industrial",
                2: "Ingeniería en Informática",
                3: "Ingeniería en Transporte",
                4: "Ingeniería Ferroviaria",
                5: "Ingeniería Industrial",
                6: "Licenciatura en Ciencias de la Informática"
            }
            self.menu_upd_prog.set(prog_map.get(user_data.get("cpa_id"), "Ingeniería en Informática"))
            
            self.menu_upd_vigencia.set("Activo" if user_data.get("vigencia") == 1 else "Inactivo")
            
            self.upd_user_status_lbl.configure(
                text=f"EXPEDIENTE DE '{user_data['nombre']}' CARGADO CORRECTAMENTE",
                text_color=COLOR_PRIMARY
            )
        else:
            self.upd_user_status_lbl.configure(
                text="ERROR: MATRÍCULA NO ENCONTRADA EN EL SERVIDOR",
                text_color=COLOR_ALERT
            )

    def execute_user_record_update(self):
        target = self.entry_update_search.get().strip()
        nom = self.entry_upd_nombre.get().strip()
        pat = self.entry_upd_pat.get().strip()
        fech_naci = self.entry_upd_fech_naci.get().strip()
        curp = self.entry_upd_curp.get().strip()

        if nom == "" or pat == "" or fech_naci == "" or curp == "":
            self.upd_user_status_lbl.configure(text="ERROR: TODOS LOS CAMPOS SON REQUERIDOS", text_color=COLOR_ALERT)
            return

        roles_id = self.map_role_id(self.menu_upd_rol.get())
        cpa_id = self.map_cpa_id(self.menu_upd_prog.get())
        vigencia = 1 if self.menu_upd_vigencia.get() == "Activo" else 0
        sexo = "M" if "Masculino" in self.menu_upd_sex.get() else "F"
        turno = self.menu_upd_turno.get()[0]

        # Prepare update dict
        update_payload = {
            "nombre": nom.upper(),
            "ap_pat": pat.upper(),
            "ap_mat": self.entry_upd_mat.get().strip().upper() or None,
            "fech_naci": fech_naci,
            "curp": curp.upper(),
            "sexo": sexo,
            "turno": turno,
            "vigencia": vigencia,
            "roles_id": roles_id,
            "cpa_id": cpa_id,
            "matricula": int(target) if target.isdigit() else None
        }

        # Update API first
        if self.current_updating_id:
            self.upd_user_status_lbl.configure(text="ENVIANDO CAMBIOS AL SERVIDOR...", text_color=COLOR_ACCENT)
            self.update()
            
            success, response = api_client.update_usuario(self.current_updating_id, update_payload)
            if not success:
                self.upd_user_status_lbl.configure(text=f"FALLO DE SERVIDOR AL ACTUALIZAR: {response}", text_color=COLOR_ALERT)
                return
        else:
            self.upd_user_status_lbl.configure(text="ERROR: NO SE HA CARGADO NINGÚN REGISTRO DESDE EL SERVIDOR", text_color=COLOR_ALERT)
            return

        self.upd_user_status_lbl.configure(
            text=f"EXPEDIENTE DE '{nom.upper()}' ACTUALIZADO SATISFACTORIAMENTE EN EL SERVIDOR",
            text_color=COLOR_PRIMARY
        )
        
        # Clear fields
        for entry in [self.entry_upd_nombre, self.entry_upd_pat, self.entry_upd_mat, self.entry_upd_curp, self.entry_upd_fech_naci]:
            entry.delete(0, tk.END)
        self.current_updating_id = None

    def execute_user_record_delete(self):
        if not self.current_updating_id:
            self.upd_user_status_lbl.configure(text="ERROR: NO SE HA CARGADO NINGÚN REGISTRO DESDE EL SERVIDOR", text_color=COLOR_ALERT)
            return

        is_online = api_client.check_health()
        if not is_online:
            self.upd_user_status_lbl.configure(text="ERROR: SERVIDOR FUERA DE LÍNEA", text_color=COLOR_ALERT)
            return

        self.upd_user_status_lbl.configure(text="ELIMINANDO USUARIO DEL SERVIDOR...", text_color=COLOR_ACCENT)
        self.update()

        success, response = api_client.eliminar_usuario(self.current_updating_id)
        if success:
            self.upd_user_status_lbl.configure(
                text="EXPEDIENTE ELIMINADO LOGICAMENTE (DESACTIVADO CORECTAMENTE)",
                text_color=COLOR_PRIMARY
            )
            # Clear fields
            for entry in [self.entry_upd_nombre, self.entry_upd_pat, self.entry_upd_mat, self.entry_upd_curp, self.entry_upd_fech_naci]:
                entry.delete(0, tk.END)
            self.current_updating_id = None
        else:
            self.upd_user_status_lbl.configure(text=f"FALLO DE SERVIDOR AL ELIMINAR: {response}", text_color=COLOR_ALERT)

