"""
Clase base abstracta para controladores de cámara
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from PIL import Image


class BaseCamera(ABC):
    """Clase base para todos los controladores de cámara"""

    def __init__(self):
        self.is_connected = False
        self.camera_info = {}

    @abstractmethod
    def connect(self) -> bool:
        """Conecta con la cámara"""
        pass

    @abstractmethod
    def disconnect(self):
        """Desconecta de la cámara"""
        pass

    @abstractmethod
    def capture(self) -> Optional[Image.Image]:
        """Captura una imagen y retorna un objeto PIL Image"""
        pass

    @abstractmethod
    def get_preview(self) -> Optional[Image.Image]:
        """Obtiene una vista previa en tiempo real"""
        pass

    @abstractmethod
    def get_settings(self) -> Dict:
        """Obtiene las configuraciones disponibles"""
        pass

    @abstractmethod
    def set_setting(self, setting: str, value) -> bool:
        """Configura un parámetro de la cámara"""
        pass

    def get_camera_info(self) -> Dict:
        """Retorna información de la cámara"""
        return self.camera_info
