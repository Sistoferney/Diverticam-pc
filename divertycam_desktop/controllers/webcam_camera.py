"""
Controlador para cámaras web (USB webcam)
"""
import logging
import cv2
import numpy as np
from typing import Optional, Dict
from PIL import Image

from .base_camera import BaseCamera

logger = logging.getLogger(__name__)


class WebcamCamera(BaseCamera):
    """Controlador para cámaras web estándar usando OpenCV"""

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.capture_device = None
        self.camera_info = {
            'type': 'webcam',
            'index': camera_index,
            'name': f'Webcam {camera_index}'
        }

    def connect(self) -> bool:
        """Conecta con la webcam"""
        try:
            self.capture_device = cv2.VideoCapture(self.camera_index)

            if not self.capture_device.isOpened():
                logger.error(f"No se pudo abrir la webcam {self.camera_index}")
                return False

            # Configurar resolución por defecto
            self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            # Leer frame de prueba
            ret, _ = self.capture_device.read()
            if not ret:
                logger.error("No se pudo leer de la webcam")
                self.capture_device.release()
                return False

            self.is_connected = True
            logger.info(f"Webcam {self.camera_index} conectada correctamente")
            return True

        except Exception as e:
            logger.error(f"Error conectando webcam: {e}")
            return False

    def disconnect(self):
        """Desconecta la webcam"""
        try:
            if self.capture_device:
                self.capture_device.release()
                self.capture_device = None
            self.is_connected = False
            logger.info("Webcam desconectada")
        except Exception as e:
            logger.error(f"Error desconectando webcam: {e}")

    def capture(self) -> Optional[Image.Image]:
        """Captura una imagen de la webcam"""
        if not self.is_connected or not self.capture_device:
            logger.error("Webcam no conectada")
            return None

        try:
            ret, frame = self.capture_device.read()

            if not ret or frame is None:
                logger.error("No se pudo capturar frame de la webcam")
                return None

            # Convertir BGR (OpenCV) a RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convertir a PIL Image
            image = Image.fromarray(frame_rgb)

            logger.info(f"Imagen capturada: {image.size}")
            return image

        except Exception as e:
            logger.error(f"Error capturando imagen: {e}")
            return None

    def get_preview(self) -> Optional[Image.Image]:
        """Obtiene un frame de preview (igual que capturar para webcam)"""
        return self.capture()

    def get_settings(self) -> Dict:
        """Obtiene configuraciones disponibles de la webcam"""
        if not self.is_connected:
            return {}

        try:
            width = int(self.capture_device.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.capture_device.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self.capture_device.get(cv2.CAP_PROP_FPS))

            return {
                'resolution': f'{width}x{height}',
                'fps': fps,
                'brightness': self.capture_device.get(cv2.CAP_PROP_BRIGHTNESS),
                'contrast': self.capture_device.get(cv2.CAP_PROP_CONTRAST),
                'saturation': self.capture_device.get(cv2.CAP_PROP_SATURATION),
            }

        except Exception as e:
            logger.error(f"Error obteniendo configuraciones: {e}")
            return {}

    def set_setting(self, setting: str, value) -> bool:
        """Configura un parámetro de la webcam"""
        if not self.is_connected or not self.capture_device:
            return False

        try:
            setting_map = {
                'resolution': self._set_resolution,
                'brightness': lambda v: self.capture_device.set(cv2.CAP_PROP_BRIGHTNESS, v),
                'contrast': lambda v: self.capture_device.set(cv2.CAP_PROP_CONTRAST, v),
                'saturation': lambda v: self.capture_device.set(cv2.CAP_PROP_SATURATION, v),
            }

            if setting in setting_map:
                result = setting_map[setting](value)
                logger.info(f"Configuración {setting} = {value}")
                return result if isinstance(result, bool) else True

            logger.warning(f"Configuración no soportada: {setting}")
            return False

        except Exception as e:
            logger.error(f"Error configurando {setting}: {e}")
            return False

    def _set_resolution(self, resolution_str: str) -> bool:
        """Configura la resolución de la cámara"""
        try:
            # Formato esperado: "1280x720"
            width, height = map(int, resolution_str.split('x'))
            self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            return True
        except Exception as e:
            logger.error(f"Error configurando resolución: {e}")
            return False

    @staticmethod
    def list_available_cameras() -> list:
        """Lista las webcams disponibles en el sistema"""
        available = []

        for i in range(10):  # Probar hasta 10 cámaras
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available.append({
                        'index': i,
                        'type': 'webcam',
                        'name': f'Webcam {i}'
                    })
                cap.release()

        return available
