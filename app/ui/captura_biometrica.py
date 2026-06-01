import os
import time
import customtkinter as ctk
from PIL import Image

try:
    import cv2
    _OPENCV_OK = True
except ImportError:
    _OPENCV_OK = False

try:
    import face_recognition
    _FACE_REC_OK = True
except ImportError:
    _FACE_REC_OK = False


class CapturaBiometrica(ctk.CTkToplevel):
    """
    Ventana modal de captura biométrica integrada en CustomTkinter.

    Uso:
        ventana = CapturaBiometrica(
            master=self,
            temp_filename="temp_captura.jpg",
            on_capture=callback_con_path,  # recibe str|None
        )
    """

    # Intervalo de refresco del video (≈66 fps teórico, limitado por cap.read)
    _REFRESH_MS = 15

    def __init__(
        self,
        master,
        temp_filename: str = "temp_captura.jpg",
        on_capture=None,
        titulo: str = "Captura Biométrica — SAFIPN",
    ):
        super().__init__(master)

        # ── Configuración de la ventana ──────────────────────────────
        self.title(titulo)
        self.geometry("700x560")
        self.resizable(False, False)
        self.configure(fg_color="#020204")
        self.attributes("-topmost", True)

        # ── Estado interno ───────────────────────────────────────────
        self._temp_filename = temp_filename
        self._on_capture = on_capture
        self._after_id = None          
        self._cap = None               
        self._last_frame_rgb = None    
        self._resultado = None         
        self._cerrado = False          
        self._ctk_image_ref = None    

        # ── Protocolo de cierre blindado ─────────────────────────────
        self.protocol("WM_DELETE_WINDOW", self.cerrar_limpio)

        # ── Construir UI ─────────────────────────────────────────────
        self._build_ui()

        # ── Abrir la cámara ──────────────────────────────────────────
        if not self._abrir_camara():
            self._set_mensaje("ERROR: No se pudo abrir la cámara.", "#FF007F")
            return

        # ── Bind de teclado ──────────────────────────────────────────
        self.bind("<space>", self._on_space)
        self.bind("<Escape>", lambda e: self.cerrar_limpio())

        # ── Arrancar loop de video ───────────────────────────────────
        self._actualizar_frame()

    # ─────────────────────────────────────────────────────────────────
    # UI
    # ─────────────────────────────────────────────────────────────────

    def _build_ui(self):
        """Construye los widgets de la ventana."""

        # Título superior
        ctk.CTkLabel(
            self,
            text="> CANAL_DE_CAPTURA_FACIAL",
            font=("Consolas", 14, "bold"),
            text_color="#00FF66",
        ).pack(anchor="w", padx=20, pady=(15, 5))

        # Frame contenedor del video
        self._video_frame = ctk.CTkFrame(
            self,
            fg_color="#0D0E15",
            border_width=2,
            border_color="#FF007F",
            corner_radius=0,
        )
        self._video_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        # Label donde se renderiza cada frame
        self._video_label = ctk.CTkLabel(
            self._video_frame, text="Inicializando cámara..."
        )
        self._video_label.pack(fill="both", expand=True)

        # Barra de mensajes inferior
        self._msg_frame = ctk.CTkFrame(
            self, fg_color="#121418", height=50,
            border_width=1.5, border_color="#00FF66", corner_radius=0,
        )
        self._msg_frame.pack(fill="x", padx=20, pady=(0, 15))
        self._msg_frame.pack_propagate(False)

        self._msg_label = ctk.CTkLabel(
            self._msg_frame,
            text="Presiona ESPACIO para capturar  |  ESC para cancelar",
            font=("Consolas", 12, "bold"),
            text_color="#00FF66",
        )
        self._msg_label.pack(expand=True)

    def _set_mensaje(self, texto: str, color: str = "#00FF66"):
        """Actualiza el banner de mensaje inferior."""
        if self.winfo_exists():
            self._msg_label.configure(text=texto, text_color=color)

    # ─────────────────────────────────────────────────────────────────
    # CÁMARA — Inicialización segura (V4L2)
    # ─────────────────────────────────────────────────────────────────

    def _abrir_camara(self) -> bool:
        """
        Abre la cámara con cv2.CAP_V4L2 (Linux).
        Fallback a backend por defecto si V4L2 falla.
        """
        if not _OPENCV_OK:
            print("[CapturaBiometrica] OpenCV no disponible.")
            return False

        self._cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if not self._cap.isOpened():
            print("[CapturaBiometrica] V4L2 falló, intentando backend default...")
            self._cap = cv2.VideoCapture(0)

        if not self._cap.isOpened():
            print("[CapturaBiometrica] No se pudo abrir ninguna cámara.")
            self._cap = None
            return False

        # Configurar resolución razonable
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[CapturaBiometrica] Cámara abierta correctamente.")
        return True

    # ─────────────────────────────────────────────────────────────────
    # LOOP ASÍNCRONO — Renderizado frame-by-frame via .after()
    # ─────────────────────────────────────────────────────────────────

    def _actualizar_frame(self):
        """
        Lee un frame de la cámara, lo convierte a PIL Image y lo muestra
        en el CTkLabel.  Se re-programa a sí misma con .after().
        """
        if self._cerrado or self._cap is None:
            return

        ret, frame_bgr = self._cap.read()

        if ret and frame_bgr is not None:
            # Espejo horizontal (más natural para el usuario)
            frame_bgr = cv2.flip(frame_bgr, 1)

            # BGR → RGB para PIL
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            self._last_frame_rgb = frame_rgb

            # Numpy array → PIL Image → CTkImage
            pil_img = Image.fromarray(frame_rgb)

            # Ajustar al tamaño del contenedor
            display_w = max(self._video_frame.winfo_width() - 10, 640)
            display_h = max(self._video_frame.winfo_height() - 10, 440)
            ctk_img = ctk.CTkImage(dark_image=pil_img, size=(display_w, display_h))

            self._video_label.configure(image=ctk_img, text="")
            self._ctk_image_ref = ctk_img  # Evitar garbage collection

        # Re-programar el siguiente frame
        self._after_id = self.after(self._REFRESH_MS, self._actualizar_frame)

    # ─────────────────────────────────────────────────────────────────
    # CAPTURA POR TECLADO — Tecla Espacio
    # ─────────────────────────────────────────────────────────────────

    def _on_space(self, event=None):
        """
        Al presionar ESPACIO:
        1. Convierte el frame actual a RGB.
        2. Usa face_recognition para buscar rostros.
        3. Si hay exactamente 1 rostro → guarda como temp y cierra.
        """
        if self._last_frame_rgb is None:
            self._set_mensaje("Sin frame disponible. Espere...", "#FFFF00")
            return

        if not _FACE_REC_OK:
            self._set_mensaje("ERROR: face_recognition no instalado.", "#FF007F")
            return

        self._set_mensaje("Analizando rostro...", "#FFFF00")
        self.update_idletasks()  # Forzar redibujado del mensaje

        # face_recognition trabaja con numpy RGB (ya lo tenemos)
        rgb_frame = self._last_frame_rgb
        locations = face_recognition.face_locations(rgb_frame)

        if len(locations) == 1:
            # ── Rostro válido: dibujar rectángulo de confirmación ────
            top, right, bottom, left = locations[0]
            pil_confirm = Image.fromarray(rgb_frame).copy()

            # Dibujar rectángulo verde sobre la imagen de confirmación
            from PIL import ImageDraw
            draw = ImageDraw.Draw(pil_confirm)
            draw.rectangle(
                [(left, top), (right, bottom)],
                outline="#00FF66", width=3
            )

            ctk_confirm = ctk.CTkImage(
                dark_image=pil_confirm,
                size=(
                    max(self._video_frame.winfo_width() - 10, 640),
                    max(self._video_frame.winfo_height() - 10, 440),
                ),
            )
            self._video_label.configure(image=ctk_confirm, text="")
            self._ctk_image_ref = ctk_confirm
            self._set_mensaje("✅ ROSTRO CAPTURADO — Guardando...", "#00FF66")
            self.update_idletasks()

            # Guardar como BGR (estándar OpenCV/JPEG)
            frame_bgr = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(self._temp_filename, frame_bgr)
            self._resultado = self._temp_filename
            print(f"[CapturaBiometrica] Rostro guardado en: {self._temp_filename}")

            # Pequeña pausa visual antes de cerrar
            self.after(600, self.cerrar_limpio)

        elif len(locations) > 1:
            self._set_mensaje(
                f"⚠ {len(locations)} rostros detectados. Solo debe haber 1.",
                "#FFFF00",
            )
        else:
            self._set_mensaje(
                "⚠ Ningún rostro detectado. Reposiciónese e intente de nuevo.",
                "#FFFF00",
            )

    # ─────────────────────────────────────────────────────────────────
    # PROTOCOLO DE DESTRUCCIÓN BLINDADO
    # ─────────────────────────────────────────────────────────────────

    def cerrar_limpio(self):
        """
        Cierre seguro que evita deadlocks con uvcvideo en Linux:
        1. Cancela el callback de .after()
        2. Libera la cámara (cap.release())
        3. Espera 0.4s para que el bus USB apague el foco
        4. Invoca el callback con el resultado
        5. Destruye la ventana
        """
        if self._cerrado:
            return
        self._cerrado = True

        # 1. Cancelar el callback pendiente de .after()
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        # 2. Liberar la cámara
        if self._cap is not None:
            try:
                self._cap.release()
                print("[CapturaBiometrica] Cámara liberada correctamente.")
            except Exception as e:
                print(f"[CapturaBiometrica] Error al liberar cámara: {e}")
            self._cap = None

        # 3. Esperar a que el bus USB de Linux desactive el LED/foco
        time.sleep(0.4)

        # 4. Invocar callback con el resultado (path o None)
        if self._on_capture is not None:
            try:
                self._on_capture(self._resultado)
            except Exception as e:
                print(f"[CapturaBiometrica] Error en callback: {e}")

        # 5. Destruir la ventana
        try:
            self.destroy()
        except Exception:
            pass
