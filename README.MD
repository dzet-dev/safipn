# SAFIPN Frontend – Interfaz Gráfica de Control de Acceso

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-1F6FEB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)

---

- **Institución:** Instituto Politécnico Nacional – UPIICSA
- **Programa:** Licenciatura en Ciencias de la Informática

---

## Descripción

Interfaz gráfica de escritorio construida con **CustomTkinter** que se conecta a la API REST del backend para gestionar el control de acceso biométrico facial en las instalaciones de la UPIICSA.

La aplicación permite registrar entradas/salidas mediante captura facial en tiempo real, consultar la bitácora de accesos y administrar la base de usuarios, todo desde una interfaz con temática cyberpunk institucional (IPN / UPIICSA).

---

## Vistas principales

| Vista | Descripción |
|-------|-------------|
| **Login** | Autenticación local por credenciales con control de roles (Administrador, Desarrollador, Diseñador). |
| **Bitácora de Accesos** | Tabla con historial de movimientos. Permite filtrar por matrícula, fecha, puerta y estatus. Consulta datos del servidor y locales. |
| **Registrar Acceso** | Captura biométrica en tiempo real. Flujo: abrir cámara → ESPACIO → validación facial → envío al backend → resultado. Soporta internos y visitantes. |
| **Gestionar Usuarios** | CRUD de usuarios: alta con captura facial, listado, activación/desactivación. Solo accesible para Administradores. |

---

## Estructura del proyecto

```
front/
├── interfaz.py              # Entry point (ejecutar con python interfaz.py)
├── Assets/
│   ├── ipn.png              # Logo IPN
│   ├── upiicsa.png          # Logo UPIICSA
│   └── safipn_logo.png      # Ícono de la aplicación
└── app/
    ├── main.py              # Inicialización de CustomTkinter y mainloop
    ├── config.py            # Paleta de colores, rutas y credenciales locales
    ├── camera.py            # CameraManager (animación mock + utilidades)
    ├── api_client.py        # Cliente HTTP hacia la API FastAPI
    ├── db.py                # Almacenamiento local de accesos
    └── ui/
        ├── mainframe.py     # Ventana principal, header, navegación lateral
        ├── login.py         # Pantalla de autenticación
        ├── bitacora.py      # Vista de bitácora con Treeview
        ├── registrar.py     # Panel de registro de acceso biométrico
        ├── gestionar.py     # Panel CRUD de usuarios
        └── captura_biometrica.py  # Ventana nativa de captura facial (CTkToplevel)
```

---

## Captura biométrica nativa

El módulo `captura_biometrica.py` integra el video de la cámara directamente en la interfaz de CustomTkinter, sin depender de ventanas de OpenCV:

- **Renderizado nativo:** cada frame se convierte a `PIL.Image` → `CTkImage` y se muestra en un `CTkLabel`.
- **Loop asíncrono:** actualización cada 15ms vía `.after()`, sin bloquear el `mainloop`.
- **Inicialización V4L2:** abre la cámara con `cv2.CAP_V4L2` (Linux) con fallback automático.
- **Validación facial:** al presionar ESPACIO, `face_recognition` verifica que haya exactamente 1 rostro.
- **Cierre seguro:** protocolo blindado que cancela callbacks, libera la cámara y espera 0.4s para el bus USB.

---

## Stack

- **Lenguaje:** Python ≥ 3.9
- **GUI:** CustomTkinter + Tkinter
- **Visión artificial:** OpenCV (`cv2.CAP_V4L2`)
- **Reconocimiento facial:** `face_recognition` + `dlib`
- **Imágenes:** Pillow (PIL)
- **HTTP:** `requests` (comunicación con la API backend)
- **Entorno:** Linux (Debian/Ubuntu)

---

## Ejecución

```bash
# Desde la raíz del proyecto, con el venv activado
source venv/bin/activate

# Ejecutar la interfaz
python front/interfaz.py
```

O usar el script de inicio rápido:

```bash
./iniciar.sh
```

---

## Sistema de roles

| Rol | Bitácora | Registrar Acceso | Gestionar Usuarios |
|-----|:--------:|:----------------:|:------------------:|
| Administrador | ✅ | ✅ | ✅ |
| Desarrollador | ✅ | ✅ | ❌ |
| Diseñador     | ✅ | ❌ | ❌ |

---

## Paleta de colores

| Token | Hex | Uso |
|-------|-----|-----|
| `COLOR_PRIMARY` | `#00FF66` | Verde UPIICSA — bordes, texto activo |
| `COLOR_ACCENT` | `#FFFF00` | Amarillo UPIICSA — alertas, estados |
| `COLOR_SECONDARY` | `#6F1D46` | Guinda IPN — botones principales |
| `COLOR_ALERT` | `#FF007F` | Guinda neón — errores, denegaciones |
| `COLOR_BG` | `#020204` | Fondo general |
| `COLOR_DARK_GRID` | `#0D0E15` | Fondo de paneles |
