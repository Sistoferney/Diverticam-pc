"""
Ventana principal del Photobooth
"""
import logging
from pathlib import Path
from typing import Optional, List
from PIL import Image

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize
from PySide6.QtGui import QPixmap, QImage, QFont

import config
from database import get_session, Evento, PhotoboothConfig, CollageSession, SessionPhoto, CollageResult, CollageTemplate
from controllers import CameraManager
from utils import CollageGenerator

logger = logging.getLogger(__name__)


class PhotoboothWindow(QMainWindow):
    """Ventana fullscreen del Photobooth"""

    # Señales
    session_completed = Signal(str)  # Emite session_id cuando termina

    def __init__(self, evento_id: int, parent=None):
        super().__init__(parent)

        self.evento_id = evento_id
        self.evento: Optional[Evento] = None
        self.config: Optional[PhotoboothConfig] = None

        # Cámara
        self.camera_manager = CameraManager()

        # Estado de la sesión
        self.session: Optional[CollageSession] = None
        self.captured_photos: List[Image.Image] = []
        self.current_frame_index = 0

        # Timers
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_preview)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_value = 0

        # Cargar configuración del evento
        if not self.load_event_config():
            QMessageBox.critical(self, "Error", "No se pudo cargar la configuración del evento")
            self.close()
            return

        self.init_ui()
        self.init_camera()

    def load_event_config(self) -> bool:
        """Carga la configuración del evento"""
        try:
            with get_session() as session:
                self.evento = session.query(Evento).filter(Evento.id == self.evento_id).first()

                if not self.evento:
                    logger.error(f"Evento {self.evento_id} no encontrado")
                    return False

                self.config = self.evento.photobooth_config

                if not self.config:
                    logger.error(f"No hay configuración de photobooth para evento {self.evento_id}")
                    return False

                logger.info(f"Configuración cargada para evento: {self.evento.nombre}")
                return True

        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return False

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"Photobooth - {self.evento.nombre}")

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Mensaje de bienvenida
        self.welcome_label = QLabel(self.config.mensaje_bienvenida)
        self.welcome_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.welcome_label.setFont(font)
        self.welcome_label.setStyleSheet(f"color: {self.config.color_texto};")
        layout.addWidget(self.welcome_label)

        # Preview de la cámara
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(QSize(800, 600))
        self.preview_label.setStyleSheet("background-color: black; border: 2px solid white;")
        self.preview_label.setScaledContents(False)
        layout.addWidget(self.preview_label)

        # Label de cuenta regresiva (superpuesto al preview)
        self.countdown_label = QLabel("", self.preview_label)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setGeometry(0, 0, 800, 600)
        font_countdown = QFont()
        font_countdown.setPointSize(120)
        font_countdown.setBold(True)
        self.countdown_label.setFont(font_countdown)
        self.countdown_label.setStyleSheet("color: white; background: transparent;")
        self.countdown_label.hide()

        # Indicador de progreso (fotos capturadas)
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignCenter)
        font_progress = QFont()
        font_progress.setPointSize(16)
        self.progress_label.setFont(font_progress)
        layout.addWidget(self.progress_label)
        self.update_progress_label()

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.btn_start = QPushButton("Iniciar Sesión")
        self.btn_start.setMinimumSize(QSize(200, 60))
        self.btn_start.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.btn_start.clicked.connect(self.start_session)
        buttons_layout.addWidget(self.btn_start)

        self.btn_capture = QPushButton("Tomar Foto")
        self.btn_capture.setMinimumSize(QSize(200, 60))
        self.btn_capture.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.btn_capture.clicked.connect(self.capture_photo)
        self.btn_capture.setEnabled(False)
        buttons_layout.addWidget(self.btn_capture)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.setMinimumSize(QSize(150, 60))
        self.btn_cancel.setStyleSheet("font-size: 18px;")
        self.btn_cancel.clicked.connect(self.cancel_session)
        self.btn_cancel.setEnabled(False)
        buttons_layout.addWidget(self.btn_cancel)

        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setMinimumSize(QSize(150, 60))
        self.btn_exit.setStyleSheet("font-size: 18px;")
        self.btn_exit.clicked.connect(self.close)
        buttons_layout.addWidget(self.btn_exit)

        layout.addLayout(buttons_layout)

        central_widget.setLayout(layout)

        # Configurar ventana
        self.resize(1024, 768)
        # self.showFullScreen()  # Descomentar para modo fullscreen

    def init_camera(self):
        """Inicializa la cámara"""
        try:
            camera_type = self.config.tipo_camara or 'webcam'
            camera_index = 0  # TODO: Obtener del config

            if self.camera_manager.connect_camera(camera_type, camera_index):
                logger.info("Cámara conectada correctamente")
                self.start_preview()
            else:
                logger.error("Error conectando con la cámara")
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "No se pudo conectar con la cámara. Algunas funciones no estarán disponibles."
                )

        except Exception as e:
            logger.error(f"Error inicializando cámara: {e}")

    def start_preview(self):
        """Inicia el preview de la cámara"""
        self.preview_timer.start(33)  # ~30 FPS

    def stop_preview(self):
        """Detiene el preview de la cámara"""
        self.preview_timer.stop()

    def update_preview(self):
        """Actualiza el frame del preview"""
        try:
            image = self.camera_manager.get_preview()

            if image:
                # Convertir PIL Image a QPixmap
                pixmap = self.pil_image_to_qpixmap(image)

                # Escalar manteniendo aspecto
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            logger.error(f"Error actualizando preview: {e}")

    @staticmethod
    def pil_image_to_qpixmap(pil_image: Image.Image) -> QPixmap:
        """Convierte una imagen PIL a QPixmap"""
        # Convertir a RGB si es necesario
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')

        # Convertir a bytes
        image_bytes = pil_image.tobytes('raw', 'RGB')

        # Crear QImage
        qimage = QImage(
            image_bytes,
            pil_image.width,
            pil_image.height,
            pil_image.width * 3,
            QImage.Format_RGB888
        )

        return QPixmap.fromImage(qimage)

    def start_session(self):
        """Inicia una nueva sesión de fotos"""
        try:
            # Crear sesión en la base de datos
            import uuid
            from database.seed import get_or_create_default_template

            session_id = str(uuid.uuid4())

            with get_session() as db_session:
                # Obtener o crear template predeterminado
                template_id = self.config.plantilla_collage_id

                if not template_id:
                    # No hay template configurado, crear uno predeterminado
                    logger.info("No hay template configurado, creando uno predeterminado...")

                    # Determinar número de fotos (puedes cambiar esto según necesites)
                    max_photos = 4

                    template_id = get_or_create_default_template(self.evento_id, max_photos)

                    if not template_id:
                        QMessageBox.critical(
                            self,
                            "Error",
                            "No se pudo crear una plantilla de collage. Por favor contacte al administrador."
                        )
                        return

                    # Actualizar config con el template creado
                    photobooth_config = db_session.query(PhotoboothConfig).filter(
                        PhotoboothConfig.evento_id == self.evento_id
                    ).first()

                    if photobooth_config:
                        photobooth_config.plantilla_collage_id = template_id
                        db_session.commit()
                        self.config.plantilla_collage_id = template_id
                        logger.info(f"Template predeterminado asignado: {template_id}")

                self.session = CollageSession(
                    session_id=session_id,
                    template_id=template_id,
                    evento_id=self.evento_id,
                    status='active'
                )

                db_session.add(self.session)
                db_session.commit()

            # Resetear estado
            self.captured_photos = []
            self.current_frame_index = 0

            # Actualizar UI
            self.btn_start.setEnabled(False)
            self.btn_capture.setEnabled(True)
            self.btn_cancel.setEnabled(True)
            self.update_progress_label()

            logger.info(f"Sesión iniciada: {session_id}")

        except Exception as e:
            logger.error(f"Error iniciando sesión: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error iniciando sesión: {str(e)}")

    def capture_photo(self):
        """Captura una foto con cuenta regresiva"""
        self.btn_capture.setEnabled(False)

        # Iniciar cuenta regresiva
        self.countdown_value = self.config.tiempo_cuenta_regresiva
        self.countdown_label.setText(str(self.countdown_value))
        self.countdown_label.show()

        self.countdown_timer.start(1000)  # 1 segundo

    def update_countdown(self):
        """Actualiza la cuenta regresiva"""
        self.countdown_value -= 1

        if self.countdown_value > 0:
            self.countdown_label.setText(str(self.countdown_value))
        else:
            # Cuenta regresiva terminada, capturar
            self.countdown_timer.stop()
            self.countdown_label.hide()
            self.perform_capture()

    def perform_capture(self):
        """Realiza la captura de la foto"""
        try:
            # Capturar imagen
            image = self.camera_manager.capture_image()

            if not image:
                QMessageBox.warning(self, "Error", "No se pudo capturar la imagen")
                self.btn_capture.setEnabled(True)
                return

            # Guardar imagen
            save_path = config.PHOTOS_DIR / f"session_{self.session.session_id}_frame_{self.current_frame_index}.jpg"
            image.save(save_path, "JPEG", quality=95)

            # Guardar en base de datos
            with get_session() as db_session:
                photo = SessionPhoto(
                    session_id=self.session.session_id,
                    frame_index=self.current_frame_index,
                    image_path=str(save_path)
                )
                db_session.add(photo)
                db_session.commit()

            # Agregar a lista local
            self.captured_photos.append(image)
            self.current_frame_index += 1

            # Actualizar UI
            self.update_progress_label()

            # Verificar si completamos todas las fotos
            max_photos = 4  # TODO: Obtener del template
            if self.current_frame_index >= max_photos:
                self.complete_session()
            else:
                # Esperar un momento y habilitar siguiente captura
                QTimer.singleShot(self.config.tiempo_entre_fotos * 1000, self.enable_next_capture)

        except Exception as e:
            logger.error(f"Error capturando foto: {e}")
            QMessageBox.critical(self, "Error", f"Error capturando foto: {str(e)}")
            self.btn_capture.setEnabled(True)

    def enable_next_capture(self):
        """Habilita el botón para la siguiente captura"""
        self.btn_capture.setEnabled(True)

    def update_progress_label(self):
        """Actualiza el label de progreso"""
        if self.session:
            max_photos = 4  # TODO: Obtener del template
            self.progress_label.setText(f"Fotos capturadas: {len(self.captured_photos)} / {max_photos}")
        else:
            self.progress_label.setText("")

    def complete_session(self):
        """Completa la sesión y genera el collage"""
        try:
            # Actualizar sesión en la base de datos
            from datetime import datetime
            with get_session() as db_session:
                session = db_session.query(CollageSession).filter(
                    CollageSession.session_id == self.session.session_id
                ).first()

                if session:
                    session.status = 'completed'
                    session.completed_at = datetime.now()
                    db_session.commit()

            logger.info(f"Sesión completada: {self.session.session_id}")

            # Mostrar mensaje
            QMessageBox.information(
                self,
                "Sesión Completada",
                "¡Fotos capturadas correctamente!\n\nGenerando collage..."
            )

            # Generar collage
            collage_path = self.generate_collage()

            if collage_path:
                # Mostrar resultado
                QMessageBox.information(
                    self,
                    "¡Listo!",
                    f"¡Collage generado exitosamente!\n\nGuardado en:\n{collage_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Advertencia",
                    "Las fotos se guardaron pero hubo un problema generando el collage."
                )

            # Emitir señal
            self.session_completed.emit(self.session.session_id)

            # Resetear para nueva sesión
            self.reset_session()

        except Exception as e:
            logger.error(f"Error completando sesión: {e}")
            QMessageBox.critical(self, "Error", f"Error completando sesión: {str(e)}")

    def generate_collage(self) -> Optional[Path]:
        """
        Genera el collage a partir de las fotos capturadas

        Returns:
            Path al collage generado, o None si hubo error
        """
        try:
            import uuid
            import json

            logger.info("Iniciando generación de collage...")

            # Obtener información de la sesión y plantilla
            with get_session() as db_session:
                # Obtener sesión con sus fotos
                session = db_session.query(CollageSession).filter(
                    CollageSession.session_id == self.session.session_id
                ).first()

                if not session:
                    logger.error("Sesión no encontrada")
                    return None

                # Obtener plantilla
                template_db = db_session.query(CollageTemplate).filter(
                    CollageTemplate.template_id == session.template_id
                ).first()

                if not template_db:
                    logger.error("Plantilla no encontrada")
                    return None

                # Convertir template_data de JSON a dict
                template_data = template_db.template_data
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)

                # Obtener fotos ordenadas por frame_index
                photos = db_session.query(SessionPhoto).filter(
                    SessionPhoto.session_id == self.session.session_id
                ).order_by(SessionPhoto.frame_index).all()

                if not photos:
                    logger.error("No hay fotos en la sesión")
                    return None

                # Obtener rutas de las imágenes
                image_paths = [photo.image_path for photo in photos]

                logger.info(f"Generando collage con {len(image_paths)} fotos")
                logger.info(f"Plantilla: {template_data.get('nombre', 'Sin nombre')}")

                # Crear generador de collage
                generator = CollageGenerator(template_data)

                # Definir ruta de salida
                collage_id = str(uuid.uuid4())
                output_filename = f"collage_{collage_id}.jpg"
                output_path = config.COLLAGES_DIR / output_filename

                # Generar collage
                result_path = generator.generate(
                    images=image_paths,
                    output_path=output_path,
                    add_border=True
                )

                if not result_path:
                    logger.error("Error generando collage")
                    return None

                # Guardar resultado en la base de datos
                collage_result = CollageResult(
                    collage_id=collage_id,
                    session_id=self.session.session_id,
                    image_path=str(result_path),
                    print_count=0,
                    share_count=0
                )

                db_session.add(collage_result)
                db_session.commit()

                logger.info(f"Collage generado exitosamente: {result_path}")
                return result_path

        except Exception as e:
            logger.error(f"Error generando collage: {e}", exc_info=True)
            return None

    def cancel_session(self):
        """Cancela la sesión actual"""
        reply = QMessageBox.question(
            self,
            "Cancelar Sesión",
            "¿Está seguro que desea cancelar la sesión actual?\n\nSe perderán las fotos capturadas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Actualizar sesión en la base de datos
                with get_session() as db_session:
                    session = db_session.query(CollageSession).filter(
                        CollageSession.session_id == self.session.session_id
                    ).first()

                    if session:
                        session.status = 'canceled'
                        db_session.commit()

                logger.info(f"Sesión cancelada: {self.session.session_id}")

                self.reset_session()

            except Exception as e:
                logger.error(f"Error cancelando sesión: {e}")

    def reset_session(self):
        """Resetea el estado para una nueva sesión"""
        self.session = None
        self.captured_photos = []
        self.current_frame_index = 0

        self.btn_start.setEnabled(True)
        self.btn_capture.setEnabled(False)
        self.btn_cancel.setEnabled(False)

        self.update_progress_label()

    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        # Detener timers
        self.preview_timer.stop()
        self.countdown_timer.stop()

        # Desconectar cámara
        self.camera_manager.cleanup()

        logger.info("Photobooth cerrado")
        event.accept()
