"""
Gestor de cámaras - Factory pattern para diferentes tipos de cámara
"""
import logging
from typing import Optional, Dict, List
from enum import Enum

from .base_camera import BaseCamera
from .webcam_camera import WebcamCamera

logger = logging.getLogger(__name__)


class CameraType(Enum):
    """Tipos de cámara soportados"""
    WEBCAM = "webcam"
    NIKON_DSLR = "nikon_dslr"
    USB_PTP = "usb_ptp"
    WINDOWS_CAMERA = "windows_camera"


class CameraManager:
    """Gestor central para todos los tipos de cámara"""

    def __init__(self):
        self.current_camera: Optional[BaseCamera] = None
        self.camera_type: Optional[CameraType] = None

    def detect_cameras(self) -> List[Dict]:
        """Detecta todas las cámaras disponibles en el sistema"""
        cameras = []

        # Detectar webcams
        try:
            webcams = WebcamCamera.list_available_cameras()
            cameras.extend(webcams)
        except Exception as e:
            logger.error(f"Error detectando webcams: {e}")

        # TODO: Detectar cámaras PTP/DSLR cuando estén implementadas
        # try:
        #     ptp_cameras = PTPCamera.list_available_cameras()
        #     cameras.extend(ptp_cameras)
        # except Exception as e:
        #     logger.error(f"Error detectando cámaras PTP: {e}")

        return cameras

    def create_camera(self, camera_type: str, camera_index: int = 0, resolution: str = '1280x720', **kwargs) -> Optional[BaseCamera]:
        """
        Crea una instancia de cámara según el tipo

        Args:
            camera_type: Tipo de cámara ('webcam', 'nikon_dslr', etc.)
            camera_index: Índice de la cámara (para webcams)
            resolution: Resolución de la cámara (ej: '1280x720', '1920x1080')
            **kwargs: Parámetros adicionales específicos del tipo de cámara

        Returns:
            Instancia de BaseCamera o None si hay error
        """
        try:
            if camera_type == CameraType.WEBCAM.value:
                return WebcamCamera(camera_index, resolution=resolution)

            elif camera_type == CameraType.NIKON_DSLR.value:
                # TODO: Implementar cuando esté listo
                logger.warning("Cámaras Nikon DSLR aún no implementadas")
                return None

            elif camera_type == CameraType.USB_PTP.value:
                # TODO: Implementar cuando esté listo
                logger.warning("Cámaras USB PTP aún no implementadas")
                return None

            elif camera_type == CameraType.WINDOWS_CAMERA.value:
                # TODO: Implementar cuando esté listo
                logger.warning("Cámaras Windows aún no implementadas")
                return None

            else:
                logger.error(f"Tipo de cámara no soportado: {camera_type}")
                return None

        except Exception as e:
            logger.error(f"Error creando cámara {camera_type}: {e}")
            return None

    def connect_camera(self, camera_type: str, camera_index: int = 0, resolution: str = '1280x720', **kwargs) -> bool:
        """
        Conecta con una cámara

        Args:
            camera_type: Tipo de cámara
            camera_index: Índice de la cámara
            resolution: Resolución de la cámara
            **kwargs: Parámetros adicionales

        Returns:
            True si la conexión fue exitosa
        """
        try:
            # Desconectar cámara anterior si existe
            if self.current_camera:
                self.disconnect_camera()

            # Crear nueva cámara
            camera = self.create_camera(camera_type, camera_index, resolution=resolution, **kwargs)

            if not camera:
                logger.error(f"No se pudo crear cámara {camera_type}")
                return False

            # Intentar conectar
            if camera.connect():
                self.current_camera = camera
                self.camera_type = CameraType(camera_type)
                logger.info(f"Cámara {camera_type} conectada correctamente")
                return True
            else:
                logger.error(f"No se pudo conectar con la cámara {camera_type}")
                return False

        except Exception as e:
            logger.error(f"Error conectando cámara: {e}")
            return False

    def disconnect_camera(self):
        """Desconecta la cámara actual"""
        if self.current_camera:
            try:
                self.current_camera.disconnect()
                logger.info("Cámara desconectada")
            except Exception as e:
                logger.error(f"Error desconectando cámara: {e}")
            finally:
                self.current_camera = None
                self.camera_type = None

    def is_connected(self) -> bool:
        """Verifica si hay una cámara conectada"""
        return self.current_camera is not None and self.current_camera.is_connected

    def get_current_camera(self) -> Optional[BaseCamera]:
        """Retorna la cámara actual"""
        return self.current_camera

    def capture_image(self):
        """Captura una imagen con la cámara actual"""
        if not self.is_connected():
            logger.error("No hay cámara conectada")
            return None

        try:
            return self.current_camera.capture()
        except Exception as e:
            logger.error(f"Error capturando imagen: {e}")
            return None

    def get_preview(self):
        """Obtiene preview de la cámara actual"""
        if not self.is_connected():
            return None

        try:
            return self.current_camera.get_preview()
        except Exception as e:
            logger.error(f"Error obteniendo preview: {e}")
            return None

    def get_camera_settings(self) -> Dict:
        """Obtiene las configuraciones de la cámara actual"""
        if not self.is_connected():
            return {}

        try:
            return self.current_camera.get_settings()
        except Exception as e:
            logger.error(f"Error obteniendo configuraciones: {e}")
            return {}

    def set_camera_setting(self, setting: str, value) -> bool:
        """Configura un parámetro de la cámara actual"""
        if not self.is_connected():
            return False

        try:
            return self.current_camera.set_setting(setting, value)
        except Exception as e:
            logger.error(f"Error configurando {setting}: {e}")
            return False

    def cleanup(self):
        """Limpia recursos"""
        self.disconnect_camera()
