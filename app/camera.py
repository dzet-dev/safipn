import os
import time
from PIL import Image, ImageDraw

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False


class CameraManager:
    def __init__(self):
        self.cap = None
        self.is_active = False

        # Mock scanner state
        self.scan_line_y = 10
        self.scan_direction = 1

    # ─────────────────────────────────────────────────────────────────
    # Live preview (used by the mock animation only)
    # ─────────────────────────────────────────────────────────────────

    def start(self) -> bool:
        """No longer opens a physical camera — mock animation only."""
        self.is_active = True
        return False

    def stop(self):
        self.is_active = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def read_frame(self):
        """Not used by current UI — kept for compatibility."""
        return False, None, False

    def save_current_frame(self, filepath: str) -> bool:
        """Not used by current UI — kept for compatibility."""
        return False

    # ─────────────────────────────────────────────────────────────────
    # Mock cyberpunk animation frame
    # ─────────────────────────────────────────────────────────────────

    def get_mock_frame(self, is_guest=False, primary_color="#00FF66", accent_color="#FFFF00"):
        img = Image.new("RGB", (640, 480), "#020204")
        draw = ImageDraw.Draw(img)

        # Background grid
        for x in range(0, 640, 40):
            draw.line((x, 0, x, 480), fill="#0d1117", width=1)
        for y in range(0, 480, 40):
            draw.line((0, y, 640, y), fill="#0d1117", width=1)

        if is_guest:
            draw.rectangle((120, 90, 520, 390), outline=accent_color, width=2)
            draw.rectangle((270, 200, 370, 300), fill="#0D0E15", outline=accent_color, width=2)
        else:
            draw.rectangle((120, 90, 520, 390), outline=primary_color, width=2)
            self.scan_line_y += 6 * self.scan_direction
            if self.scan_line_y >= 380:
                self.scan_line_y = 380
                self.scan_direction = -1
            elif self.scan_line_y <= 100:
                self.scan_line_y = 100
                self.scan_direction = 1
            draw.line((125, self.scan_line_y, 515, self.scan_line_y), fill=primary_color, width=3)

        return img

    # ─────────────────────────────────────────────────────────────────
    # Popup capture  (idéntico a cli.py)
    # ─────────────────────────────────────────────────────────────────

    def capture_face_with_popup(
        self,
        title: str = "Captura Biometrica",
        temp_filename: str = "temp_captura.jpg",
        mensaje_instruccion: str = "Acomodate y presiona ESPACIO.  (q=salir)"
    ) -> str | None:
        """
        Opens a separate OpenCV window (identical to cli.py).
        User presses SPACE → face validated with face_recognition → saved to temp_filename.
        Returns the path on success, None on cancel/failure.

        BUG FIX: uses cv2.CAP_V4L2 on Linux so the device is fully released
        between calls, preventing the camera from getting stuck on re-use.
        """
        if not OPENCV_AVAILABLE:
            print("[ERROR] OpenCV no disponible.")
            return None

        try:
            import face_recognition
        except ImportError:
            print("[ERROR] face_recognition no instalado.")
            return None

        # ── Open camera (V4L2 on Linux, fallback to default) ────────
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] No se pudo abrir la cámara web.")
            return None

        rostro_valido = False
        mensaje = mensaje_instruccion

        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("[ERROR] No se pudo leer frame de la cámara.")
                    break

                frame = cv2.flip(frame, 1)
                cv2.putText(frame, mensaje, (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow(title, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == 32:  # SPACE
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    print("[Cámara] Analizando rostro...")
                    locations = face_recognition.face_locations(rgb)

                    if len(locations) == 1:
                        top, right, bottom, left = locations[0]
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        cv2.putText(frame, "ROSTRO CAPTURADO", (20, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.imshow(title, frame)
                        cv2.waitKey(700)
                        cv2.imwrite(temp_filename, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
                        rostro_valido = True
                        break
                    elif len(locations) > 1:
                        mensaje = "Multiples rostros detectados. Intente de nuevo."
                    else:
                        mensaje = "Ningun rostro detectado. Intente de nuevo."
        finally:
            # Always release properly so the device isn't locked for the next call
            cap.release()
            try:
                cv2.destroyWindow(title)
            except Exception:
                pass
            cv2.waitKey(1)          # flush pending events
            time.sleep(0.4)         # give the OS time to free /dev/videoX

        return temp_filename if rostro_valido else None


# Singleton
camera_manager = CameraManager()
