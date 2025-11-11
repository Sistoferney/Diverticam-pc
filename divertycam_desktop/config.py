"""
Configuración de DivertyCam Desktop
"""
import os
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MEDIA_DIR = BASE_DIR / "media"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios si no existen
for directory in [DATA_DIR, MEDIA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Base de datos SQLite
DATABASE_URL = f"sqlite:///{DATA_DIR / 'divertycam.db'}"

# Configuración de la aplicación
APP_NAME = "DivertyCam Desktop"
APP_VERSION = "1.0.0"
COMPANY_NAME = "DivertyCam"

# Configuración de cámara
CAMERA_SETTINGS = {
    'default_resolution': '1280x720',
    'default_camera_type': 'webcam',
    'capture_timeout': 30,
    'connection_timeout': 10,
}

# Configuración de impresión
PRINT_SETTINGS = {
    'default_paper_size': '10x15',
    'default_quality': 'high',
    'auto_print': False,
}

# Configuración de photobooth
PHOTOBOOTH_SETTINGS = {
    'countdown_time': 3,
    'time_between_photos': 3,
    'default_max_photos': 4,
}

# Rutas de medios
TEMP_DIR = MEDIA_DIR / "temp"
COLLAGES_DIR = MEDIA_DIR / "collages"
PHOTOS_DIR = MEDIA_DIR / "photos"
BACKGROUNDS_DIR = MEDIA_DIR / "backgrounds"

# Crear subdirectorios de media
for media_dir in [TEMP_DIR, COLLAGES_DIR, PHOTOS_DIR, BACKGROUNDS_DIR]:
    media_dir.mkdir(parents=True, exist_ok=True)

# Logging
LOG_FILE = LOGS_DIR / "divertycam.log"
LOG_LEVEL = "INFO"

# Configuración de licencia (para futuro)
LICENSE_SERVER_URL = "https://api.divertycam.com/validate"
LICENSE_CHECK_INTERVAL_DAYS = 7
