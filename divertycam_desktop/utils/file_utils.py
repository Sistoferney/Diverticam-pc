"""
Utilidades para manejo de archivos
"""
import shutil
import uuid
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Rutas base
MEDIA_DIR = Path(__file__).parent.parent / "media"
BACKGROUNDS_DIR = MEDIA_DIR / "backgrounds"
COLLAGES_DIR = MEDIA_DIR / "collages"
PHOTOS_DIR = MEDIA_DIR / "photos"
TEMP_DIR = MEDIA_DIR / "temp"


def ensure_media_directories():
    """Asegura que existan todas las carpetas de media"""
    for directory in [MEDIA_DIR, BACKGROUNDS_DIR, COLLAGES_DIR, PHOTOS_DIR, TEMP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def copy_background_image(source_path: str) -> str:
    """
    Copia una imagen de fondo a la carpeta backgrounds

    Args:
        source_path: Ruta de la imagen original

    Returns:
        Ruta relativa de la imagen copiada (desde la carpeta del proyecto)
    """
    try:
        ensure_media_directories()

        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {source_path}")

        # Generar nombre único para evitar conflictos
        extension = source.suffix
        filename = f"{uuid.uuid4()}{extension}"
        destination = BACKGROUNDS_DIR / filename

        # Copiar archivo
        shutil.copy2(source, destination)

        logger.info(f"Imagen copiada: {source} -> {destination}")

        # Retornar ruta relativa desde el directorio del proyecto
        project_root = Path(__file__).parent.parent
        relative_path = destination.relative_to(project_root)

        return str(relative_path)

    except Exception as e:
        logger.error(f"Error copiando imagen de fondo: {e}", exc_info=True)
        raise


def get_absolute_path(relative_path: str) -> Path:
    """
    Convierte una ruta relativa a absoluta

    Args:
        relative_path: Ruta relativa desde la carpeta del proyecto

    Returns:
        Path absoluto
    """
    if not relative_path:
        return None

    project_root = Path(__file__).parent.parent
    absolute_path = project_root / relative_path

    return absolute_path if absolute_path.exists() else None


def delete_background_image(relative_path: str) -> bool:
    """
    Elimina una imagen de fondo

    Args:
        relative_path: Ruta relativa de la imagen

    Returns:
        True si se eliminó correctamente
    """
    try:
        absolute_path = get_absolute_path(relative_path)
        if absolute_path and absolute_path.exists():
            absolute_path.unlink()
            logger.info(f"Imagen eliminada: {absolute_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error eliminando imagen: {e}", exc_info=True)
        return False
