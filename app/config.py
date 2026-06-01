import os

# Base paths
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(APP_DIR, "Assets")

# Appearance settings
APPEARANCE_MODE = "dark"

# Color Palette (IPN / UPIICSA Cyberpunk Theme)
COLOR_BG = "#020204"
COLOR_PRIMARY = "#00FF66"      # Verde UPIICSA
COLOR_PRIMARY_HOVER = "#33FF99"
COLOR_ACCENT = "#FFFF00"       # Amarillo UPIICSA
COLOR_SECONDARY = "#6F1D46"    # Guinda IPN
COLOR_ALERT = "#FF007F"        # Guinda Neon
COLOR_TEXT_LIGHT = "#FFFFFF"
COLOR_DARK_GRID = "#0D0E15"
COLOR_TEXT_GLOW = "#E2F9FF"
COLOR_MUTED = "#6A7B83"

# Default Server Config
DEFAULT_API_URL = "http://localhost:8000"

# User Credentials for GUI access control (Fallback/Local)
CREDENTIALS_DB = {
    "ADMIN_SAFIPN": {"pass": "1234", "role": "Administrador"},
    "MIGUEL_DEV": {"pass": "MIGUEL2026", "role": "Desarrollador"},
    "CHRISTIAN_CAMPOS": {"pass": "DESIGNER_NET", "role": "Diseñador"}
}

def get_asset_path(filename):
    """Dynamically locates asset files in the Assets folder or app root."""
    path_assets = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(path_assets):
        return path_assets
    path_sibling = os.path.join(APP_DIR, filename)
    if os.path.exists(path_sibling):
        return path_sibling
    return filename
