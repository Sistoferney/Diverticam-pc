"""
Utilidades para DivertyCam Desktop
"""
from .collage_generator import CollageGenerator
from .collage_templates import get_default_templates, create_template
from .file_utils import (
    copy_background_image,
    get_absolute_path,
    delete_background_image,
    ensure_media_directories
)

__all__ = [
    'CollageGenerator',
    'get_default_templates',
    'create_template',
    'copy_background_image',
    'get_absolute_path',
    'delete_background_image',
    'ensure_media_directories',
]
