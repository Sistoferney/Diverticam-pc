"""
Ventana del Photobooth - Rediseño completo con flujo correcto

Flujo:
1. Pantalla de Bienvenida → "Iniciar Cámara"
2. Pantalla de Cámara con preview → "¡TOMAR FOTOS!"
3. Captura AUTOMÁTICA con intervalos
4. Pantalla de Resultado con collage
"""
import logging
import uuid
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from PIL import Image

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap, QImage, QFont, QPalette, QBrush, QColor

import config
from database import get_session, Evento, PhotoboothConfig, CollageSession, SessionPhoto, CollageResult, CollageTemplate
from controllers import CameraManager
from utils import CollageGenerator, get_absolute_path

logger = logging.getLogger(__name__)


class PhotoboothWindow(QMainWindow):
    """Ventana del Photobooth con flujo de 3 pantallas"""

    def __init__(self, evento_id: int, parent=None):
        super().__init__(parent)

        self.evento_id = evento_id
        self.evento: Optional[Evento] = None
        self.photobooth_config: Optional[PhotoboothConfig] = None

        # Cámara
        self.camera_manager = CameraManager()
        self.camera = None

        # Datos de sesión
        self.session_id = None
        self.captured_photos: List[Image.Image] = []
        self.current_photo_index = 0
        self.total_photos = 0

        # Timers
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self.update_camera_preview)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_value = 0

        # Cargar datos del evento
        if not self.load_evento_data():
            QMessageBox.critical(self, "Error", "No se pudo cargar la configuración del evento")
            self.close()
            return

        # Inicializar UI
        self.init_ui()

    def load_evento_data(self) -> bool:
        """Carga los datos del evento y su configuración"""
        try:
            with get_session() as session:
                from sqlalchemy.orm import joinedload

                # Cargar evento con cliente
                evento = session.query(Evento).options(
                    joinedload(Evento.cliente)
                ).filter(Evento.id == self.evento_id).first()

                if not evento:
                    return False

                # Guardar datos básicos
                self.evento_nombre = evento.nombre
                self.cliente_nombre = evento.cliente.nombre_completo if evento.cliente else "Sin cliente"

                # Cargar configuración de photobooth
                pb_config = session.query(PhotoboothConfig).filter(
                    PhotoboothConfig.evento_id == self.evento_id
                ).first()

                if not pb_config:
                    # Crear configuración básica
                    pb_config = PhotoboothConfig(evento_id=self.evento_id)
                    session.add(pb_config)
                    session.commit()
                    session.refresh(pb_config)

                # Guardar configuración
                self.config_data = {
                    'mensaje_bienvenida': pb_config.mensaje_bienvenida or f"¡Bienvenido a {self.evento_nombre}!",
                    'color_texto': pb_config.color_texto or "#FFFFFF",
                    'tamano_texto': pb_config.tamano_texto or 48,
                    'imagen_fondo': pb_config.imagen_fondo,  # Agregar imagen de fondo
                    'tiempo_cuenta_regresiva': pb_config.tiempo_cuenta_regresiva or 3,
                    'tiempo_entre_fotos': pb_config.tiempo_entre_fotos or 3,
                    'tiempo_visualizacion_foto': pb_config.tiempo_visualizacion_foto or 2,
                    'plantilla_collage_id': pb_config.plantilla_collage_id,
                    'resolucion_camara': pb_config.resolucion_camara or '1280x720'
                }

                return True

        except Exception as e:
            logger.error(f"Error cargando datos del evento: {e}", exc_info=True)
            return False

    def init_ui(self):
        """Inicializa la interfaz con 3 pantallas"""
        self.setWindowTitle(f"Photobooth - {self.evento_nombre}")
        self.showFullScreen()

        # Widget central con stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Crear las 3 pantallas
        self.create_welcome_screen()
        self.create_camera_screen()
        self.create_result_screen()

        # Mostrar pantalla de bienvenida
        self.stack.setCurrentIndex(0)

    def create_welcome_screen(self):
        """Crea la pantalla de bienvenida con imagen de fondo opcional"""
        # Contenedor principal
        welcome = QWidget()
        welcome.setStyleSheet("background-color: #2b2278;")  # Color de respaldo

        # Intentar cargar imagen de fondo
        background_pixmap = None
        if self.config_data.get('imagen_fondo'):
            try:
                # Obtener ruta absoluta desde la ruta relativa guardada
                img_path = get_absolute_path(self.config_data['imagen_fondo'])
                if img_path:
                    background_pixmap = QPixmap(str(img_path))
                    logger.info(f"Imagen de fondo cargada: {img_path}")
                else:
                    logger.warning(f"Imagen de fondo no encontrada: {self.config_data['imagen_fondo']}")
            except Exception as e:
                logger.error(f"Error cargando imagen de fondo: {e}")

        # Si hay imagen, crear label de fondo con tamaño completo
        if background_pixmap:
            self.welcome_background_label = QLabel(welcome)
            self.welcome_background_label.setScaledContents(False)
            self.welcome_background_label.setAlignment(Qt.AlignCenter)

            # Escalar pixmap para cubrir toda la pantalla (modo cover)
            screen_size = self.screen().size()
            pixmap_size = background_pixmap.size()
            scale_x = screen_size.width() / pixmap_size.width()
            scale_y = screen_size.height() / pixmap_size.height()
            scale = max(scale_x, scale_y)

            scaled_pixmap = background_pixmap.scaled(
                int(pixmap_size.width() * scale),
                int(pixmap_size.height() * scale),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.welcome_background_label.setPixmap(scaled_pixmap)
            self.welcome_background_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
            self.welcome_background_label.lower()
        else:
            self.welcome_background_label = None

        # Layout principal del widget welcome
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        welcome.setLayout(main_layout)

        # Widget contenedor transparente para el contenido (encima del fondo)
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        content_widget.setLayout(layout)

        main_layout.addWidget(content_widget)

        layout.addStretch()

        # Mensaje de bienvenida
        welcome_label = QLabel(self.config_data['mensaje_bienvenida'])
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setWordWrap(True)

        font = QFont()
        font.setPointSize(self.config_data['tamano_texto'])
        font.setBold(True)
        welcome_label.setFont(font)

        welcome_label.setStyleSheet(f"color: {self.config_data['color_texto']}; padding: 40px; background-color: transparent;")
        layout.addWidget(welcome_label)

        # Subtítulo
        subtitle = QLabel("¡Captura tu mejor momento y llévate un recuerdo inolvidable!")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #FFFFFF; font-size: 24px; padding: 20px; background-color: transparent;")
        layout.addWidget(subtitle)

        layout.addStretch()

        # Botón iniciar cámara
        self.btn_start_camera = QPushButton("📷 Iniciar Cámara")
        self.btn_start_camera.setMinimumSize(300, 80)
        self.btn_start_camera.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 28px;
                font-weight: bold;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_start_camera.clicked.connect(self.start_camera)

        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(self.btn_start_camera)
        button_container.addStretch()
        layout.addLayout(button_container)

        layout.addStretch()

        # Botón cerrar (esquina superior derecha)
        close_btn = QPushButton("❌ Cerrar")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                font-size: 16px;
                border-radius: 5px;
                padding: 10px 20px;
            }
        """)
        close_btn.clicked.connect(self.close)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(close_btn)
        layout.insertLayout(0, top_bar)

        self.stack.addWidget(welcome)

    def create_camera_screen(self):
        """Crea la pantalla de cámara con preview"""
        camera = QWidget()
        layout = QVBoxLayout()
        camera.setLayout(layout)

        # Fondo negro
        camera.setAutoFillBackground(True)
        palette = camera.palette()
        palette.setColor(QPalette.Window, Qt.black)
        camera.setPalette(palette)

        # Vista previa de la cámara
        self.camera_preview_label = QLabel()
        self.camera_preview_label.setAlignment(Qt.AlignCenter)
        self.camera_preview_label.setMinimumSize(800, 600)
        self.camera_preview_label.setStyleSheet("border: 3px solid #4CAF50;")
        self.camera_preview_label.setScaledContents(False)
        layout.addWidget(self.camera_preview_label, 1)

        # Indicador de progreso
        self.progress_label = QLabel("0 / 0 fotos")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: white; font-size: 24px; padding: 10px;")
        layout.addWidget(self.progress_label)

        # Instrucciones
        self.instruction_label = QLabel()
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.setStyleSheet("color: white; font-size: 20px; padding: 10px;")
        layout.addWidget(self.instruction_label)

        # Botón iniciar sesión
        self.btn_start_session = QPushButton("📸 ¡TOMAR FOTOS!")
        self.btn_start_session.setMinimumSize(300, 80)
        self.btn_start_session.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 32px;
                font-weight: bold;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """)
        self.btn_start_session.clicked.connect(self.start_photo_session)

        button_container = QHBoxLayout()
        button_container.addStretch()
        button_container.addWidget(self.btn_start_session)
        button_container.addStretch()
        layout.addLayout(button_container)

        # Overlay de cuenta regresiva
        self.countdown_label = QLabel()
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("""
            color: #f44336;
            font-size: 120px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 20px;
            padding: 40px;
        """)
        self.countdown_label.setVisible(False)

        # Posicionar overlay en el centro
        self.countdown_label.setParent(camera)
        self.countdown_label.setGeometry(0, 0, 0, 0)  # Se ajustará dinámicamente

        self.stack.addWidget(camera)

    def create_result_screen(self):
        """Crea la pantalla de resultado"""
        result = QWidget()
        layout = QVBoxLayout()
        result.setLayout(layout)

        # Fondo
        result.setAutoFillBackground(True)
        palette = result.palette()
        palette.setColor(QPalette.Window, QColor("#2b2278"))
        result.setPalette(palette)

        # Título
        title = QLabel("¡Tu recuerdo está listo!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: white; font-size: 36px; font-weight: bold; padding: 20px;")
        layout.addWidget(title)

        # Imagen del collage
        self.collage_image_label = QLabel()
        self.collage_image_label.setAlignment(Qt.AlignCenter)
        self.collage_image_label.setScaledContents(False)
        layout.addWidget(self.collage_image_label, 1)

        # Botones
        buttons_layout = QHBoxLayout()

        self.btn_new_session = QPushButton("🔄 Nueva Sesión")
        self.btn_new_session.setMinimumSize(200, 60)
        self.btn_new_session.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.btn_new_session.clicked.connect(self.restart_session)
        buttons_layout.addWidget(self.btn_new_session)

        self.btn_print = QPushButton("🖨 Imprimir")
        self.btn_print.setMinimumSize(200, 60)
        self.btn_print.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.btn_print.clicked.connect(self.print_collage)
        buttons_layout.addWidget(self.btn_print)

        self.btn_close_result = QPushButton("❌ Volver a Eventos")
        self.btn_close_result.setMinimumSize(200, 60)
        self.btn_close_result.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        self.btn_close_result.clicked.connect(self.return_to_events)
        buttons_layout.addWidget(self.btn_close_result)

        layout.addLayout(buttons_layout)

        self.stack.addWidget(result)

    def start_camera(self):
        """Inicia la cámara y muestra la pantalla de cámara"""
        try:
            # Inicializar cámara
            resolution = self.config_data['resolucion_camara']
            self.camera = self.camera_manager.create_camera('webcam', resolution=resolution)

            if not self.camera.connect():
                QMessageBox.critical(self, "Error", "No se pudo conectar a la cámara")
                return

            # Cambiar a pantalla de cámara
            self.stack.setCurrentIndex(1)

            # Crear sesión en la base de datos
            if not self.create_session():
                QMessageBox.critical(self, "Error", "No se pudo crear la sesión")
                return

            # Iniciar preview
            self.preview_timer.start(33)  # ~30 FPS

            # Actualizar instrucciones
            self.update_instructions()

            logger.info("Cámara iniciada correctamente")

        except Exception as e:
            logger.error(f"Error iniciando cámara: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error iniciando cámara: {str(e)}")

    def create_session(self) -> bool:
        """Crea una nueva sesión de collage en la base de datos"""
        try:
            from database.seed import get_or_create_default_template

            # Obtener plantilla
            template_id = self.config_data['plantilla_collage_id']

            if not template_id:
                # Crear plantilla predeterminada
                template_id = get_or_create_default_template(self.evento_id, 4)

                if not template_id:
                    logger.error("No se pudo crear plantilla predeterminada")
                    return False

            # Obtener número de fotos de la plantilla
            with get_session() as session:
                import json

                template = session.query(CollageTemplate).filter(
                    CollageTemplate.template_id == template_id
                ).first()

                if not template:
                    logger.error("Plantilla no encontrada")
                    return False

                template_data = template.template_data
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)

                self.total_photos = template_data.get('num_photos', 4)

                # Crear sesión
                self.session_id = str(uuid.uuid4())

                collage_session = CollageSession(
                    session_id=self.session_id,
                    template_id=template_id,
                    evento_id=self.evento_id,
                    status='active'
                )

                session.add(collage_session)
                session.commit()

                logger.info(f"Sesión creada: {self.session_id}, {self.total_photos} fotos")

            # Actualizar UI
            self.current_photo_index = 0
            self.captured_photos = []
            self.update_progress()

            return True

        except Exception as e:
            logger.error(f"Error creando sesión: {e}", exc_info=True)
            return False

    def update_camera_preview(self):
        """Actualiza el preview de la cámara"""
        try:
            if not self.camera:
                return

            preview = self.camera.get_preview()
            if preview:
                # Convertir PIL Image a QPixmap
                preview_rgb = preview.convert('RGB')
                data = preview_rgb.tobytes("raw", "RGB")
                qimage = QImage(data, preview_rgb.width, preview_rgb.height, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)

                # Escalar manteniendo proporción
                scaled_pixmap = pixmap.scaled(
                    self.camera_preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                self.camera_preview_label.setPixmap(scaled_pixmap)

        except Exception as e:
            logger.error(f"Error actualizando preview: {e}")

    def update_instructions(self):
        """Actualiza las instrucciones mostradas"""
        instruction_text = (
            f"Se tomarán {self.total_photos} fotos con "
            f"{self.config_data['tiempo_entre_fotos']} segundos entre cada una"
        )
        self.instruction_label.setText(instruction_text)

    def update_progress(self):
        """Actualiza el indicador de progreso"""
        self.progress_label.setText(f"{len(self.captured_photos)} / {self.total_photos} fotos")

    def start_photo_session(self):
        """Inicia la captura automática de fotos"""
        try:
            self.btn_start_session.setEnabled(False)
            self.btn_start_session.setText("📸 Tomando fotos...")

            # Iniciar cuenta regresiva para la primera foto
            self.start_countdown()

        except Exception as e:
            logger.error(f"Error iniciando sesión de fotos: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def start_countdown(self):
        """Inicia la cuenta regresiva antes de tomar una foto"""
        self.countdown_value = self.config_data['tiempo_cuenta_regresiva']
        self.countdown_label.setText(str(self.countdown_value))

        # Centrar y mostrar overlay
        self.center_countdown_overlay()
        self.countdown_label.setVisible(True)

        self.countdown_timer.start(1000)

    def center_countdown_overlay(self):
        """Centra el overlay de cuenta regresiva"""
        parent_size = self.stack.currentWidget().size()
        overlay_size = self.countdown_label.sizeHint()

        x = (parent_size.width() - 300) // 2
        y = (parent_size.height() - 200) // 2

        self.countdown_label.setGeometry(x, y, 300, 200)

    def update_countdown(self):
        """Actualiza la cuenta regresiva"""
        self.countdown_value -= 1

        if self.countdown_value > 0:
            self.countdown_label.setText(str(self.countdown_value))
        elif self.countdown_value == 0:
            self.countdown_label.setText("¡Sonríe!")
        else:
            # Terminar countdown y capturar
            self.countdown_timer.stop()
            self.countdown_label.setVisible(False)

            # Capturar foto
            QTimer.singleShot(500, self.capture_photo)

    def capture_photo(self):
        """Captura una foto"""
        try:
            if not self.camera:
                logger.error("Cámara no disponible")
                return

            # Capturar imagen
            photo = self.camera.capture()

            if not photo:
                logger.error("No se pudo capturar la foto")
                QMessageBox.warning(self, "Error", "No se pudo capturar la foto")
                self.btn_start_session.setEnabled(True)
                self.btn_start_session.setText("📸 ¡TOMAR FOTOS!")
                return

            # Guardar foto
            self.captured_photos.append(photo)

            # Guardar en la base de datos
            self.save_photo_to_db(photo)

            # Actualizar progreso
            self.update_progress()

            logger.info(f"Foto {len(self.captured_photos)}/{self.total_photos} capturada exitosamente")

            # Intentar mostrar foto capturada durante tiempo_visualizacion_foto
            try:
                self.show_captured_photo(photo)
            except Exception as e:
                logger.error(f"Error mostrando foto: {e}", exc_info=True)

            # SIEMPRE continuar con el flujo, independiente de errores en visualización
            # Verificar si terminamos
            if len(self.captured_photos) >= self.total_photos:
                # Todas las fotos capturadas - esperar tiempo de visualización + continuar
                wait_time = self.config_data['tiempo_visualizacion_foto'] * 1000
                logger.info(f"Sesión completa. Esperando {wait_time}ms antes de generar collage")
                QTimer.singleShot(wait_time, self.finish_session)
            else:
                # Esperar tiempo de visualización + tiempo entre fotos antes de la siguiente
                tiempo_vis = self.config_data['tiempo_visualizacion_foto']
                tiempo_entre = self.config_data['tiempo_entre_fotos']
                total_wait = (tiempo_vis + tiempo_entre) * 1000
                logger.info(f"Esperando {tiempo_vis}s (visualización) + {tiempo_entre}s (entre fotos) = {total_wait}ms antes de siguiente foto")
                QTimer.singleShot(total_wait, self.continue_to_next_photo)

        except Exception as e:
            logger.error(f"Error capturando foto: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error capturando foto: {str(e)}")

    def show_captured_photo(self, photo: Image.Image):
        """Muestra la foto capturada temporalmente"""
        # VERSIÓN SIMPLIFICADA - Solo detener preview temporalmente
        try:
            # Detener el preview de cámara temporalmente
            self.preview_timer.stop()

            # Ocultar countdown
            self.countdown_label.setVisible(False)

            # TODO: Implementar visualización correcta de la foto
            # Por ahora solo mostramos un mensaje en el label del progreso
            self.progress_label.setText(f"✓ Foto {len(self.captured_photos)}/{self.total_photos} capturada")

            logger.info(f"Foto {len(self.captured_photos)} capturada. Esperando antes de continuar...")

        except Exception as e:
            logger.error(f"Error en show_captured_photo: {e}", exc_info=True)

    def continue_to_next_photo(self):
        """Continúa con la siguiente foto después de mostrar la capturada"""
        try:
            # Limpiar el preview label
            self.camera_preview_label.clear()

            # Actualizar el progreso de nuevo
            self.update_progress()

            # Reanudar preview de cámara
            self.preview_timer.start(30)  # 30ms = ~33 fps

            logger.info("Reanudando preview para siguiente foto")

            # Comenzar countdown para la siguiente foto
            self.start_countdown()

        except Exception as e:
            logger.error(f"Error continuando a siguiente foto: {e}", exc_info=True)

    def save_photo_to_db(self, photo: Image.Image):
        """Guarda la foto en la base de datos"""
        try:
            # Crear directorio si no existe
            photos_dir = config.PHOTOS_DIR / self.session_id
            photos_dir.mkdir(parents=True, exist_ok=True)

            # Guardar imagen
            photo_filename = f"photo_{len(self.captured_photos)}.jpg"
            photo_path = photos_dir / photo_filename
            photo.save(photo_path, "JPEG", quality=95)

            # Guardar en BD
            with get_session() as session:
                session_photo = SessionPhoto(
                    session_id=self.session_id,
                    frame_index=len(self.captured_photos) - 1,
                    image_path=str(photo_path)
                )

                session.add(session_photo)
                session.commit()

                logger.info(f"Foto guardada: {photo_path}")

        except Exception as e:
            logger.error(f"Error guardando foto en DB: {e}", exc_info=True)

    def finish_session(self):
        """Finaliza la sesión y genera el collage"""
        try:
            # Detener preview
            self.preview_timer.stop()

            # Actualizar sesión en BD
            with get_session() as session:
                collage_session = session.query(CollageSession).filter(
                    CollageSession.session_id == self.session_id
                ).first()

                if collage_session:
                    collage_session.status = 'completed'
                    collage_session.completed_at = datetime.now()
                    session.commit()

            logger.info("Sesión completada, generando collage...")

            # Generar collage
            collage_path = self.generate_collage()

            if collage_path:
                # Mostrar resultado
                self.show_result(collage_path)
            else:
                QMessageBox.warning(self, "Advertencia", "Hubo un problema generando el collage")
                self.restart_session()

        except Exception as e:
            logger.error(f"Error finalizando sesión: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def generate_collage(self) -> Optional[Path]:
        """Genera el collage"""
        try:
            import json

            with get_session() as session:
                # Obtener sesión y plantilla
                collage_session = session.query(CollageSession).filter(
                    CollageSession.session_id == self.session_id
                ).first()

                if not collage_session:
                    return None

                template_db = session.query(CollageTemplate).filter(
                    CollageTemplate.template_id == collage_session.template_id
                ).first()

                if not template_db:
                    return None

                # Obtener template data
                template_data = template_db.template_data
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)

                # Agregar imagen de fondo al template_data desde el modelo
                if template_db.background_image:
                    template_data['canvas']['background_image'] = template_db.background_image
                    logger.info(f"Imagen de fondo agregada al collage: {template_db.background_image}")

                # Obtener fotos
                photos = session.query(SessionPhoto).filter(
                    SessionPhoto.session_id == self.session_id
                ).order_by(SessionPhoto.frame_index).all()

                if not photos:
                    return None

                image_paths = [photo.image_path for photo in photos]

                # Generar collage
                generator = CollageGenerator(template_data)

                collage_id = str(uuid.uuid4())
                output_filename = f"collage_{collage_id}.jpg"
                output_path = config.COLLAGES_DIR / output_filename

                result_path = generator.generate(
                    images=image_paths,
                    output_path=output_path,
                    add_border=True
                )

                if not result_path:
                    return None

                # Guardar en BD
                collage_result = CollageResult(
                    collage_id=collage_id,
                    session_id=self.session_id,
                    image_path=str(result_path),
                    print_count=0,
                    share_count=0
                )

                session.add(collage_result)
                session.commit()

                logger.info(f"Collage generado: {result_path}")
                return result_path

        except Exception as e:
            logger.error(f"Error generando collage: {e}", exc_info=True)
            return None

    def show_result(self, collage_path: Path):
        """Muestra la pantalla de resultado con el collage"""
        try:
            # Cargar imagen del collage
            pixmap = QPixmap(str(collage_path))

            # Escalar manteniendo proporción
            scaled_pixmap = pixmap.scaled(
                1200, 800,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.collage_image_label.setPixmap(scaled_pixmap)

            # Guardar path para imprimir
            self.current_collage_path = collage_path

            # Cambiar a pantalla de resultado
            self.stack.setCurrentIndex(2)

        except Exception as e:
            logger.error(f"Error mostrando resultado: {e}", exc_info=True)

    def restart_session(self):
        """Reinicia para una nueva sesión"""
        # Limpiar datos
        self.session_id = None
        self.captured_photos = []
        self.current_photo_index = 0
        self.current_collage_path = None

        # Volver a pantalla de bienvenida
        self.stack.setCurrentIndex(0)

        # Detener cámara si está activa
        if self.camera:
            self.camera.disconnect()
            self.camera = None

        # Detener preview
        self.preview_timer.stop()

    def print_collage(self):
        """Imprime el collage (placeholder)"""
        QMessageBox.information(
            self,
            "Imprimir",
            "Función de impresión pendiente de implementar"
        )

    def return_to_events(self):
        """Regresa a la lista de eventos (cierra la ventana de photobooth)"""
        # Limpiar recursos
        if self.camera:
            self.camera.disconnect()
            self.camera = None

        # Detener timers
        self.preview_timer.stop()
        self.countdown_timer.stop()

        # Cerrar ventana
        self.close()

    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        # Detener timers
        self.preview_timer.stop()
        self.countdown_timer.stop()

        # Cerrar cámara
        if self.camera:
            self.camera.disconnect()

        event.accept()
