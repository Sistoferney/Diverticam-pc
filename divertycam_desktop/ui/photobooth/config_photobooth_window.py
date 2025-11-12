"""
Ventana de configuración del Photobooth
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QLineEdit, QSpinBox, QComboBox, QCheckBox,
    QColorDialog, QFileDialog, QGroupBox, QMessageBox, QScrollArea, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPixmap, QPalette, QBrush

from database import get_session, Evento, PhotoboothConfig, CollageTemplate
from utils import copy_background_image, get_absolute_path

logger = logging.getLogger(__name__)


class PreviewFrame(QWidget):
    """Widget personalizado para el preview con manejo de resize"""

    def __init__(self, parent_window, parent=None):
        super().__init__(parent)
        self.parent_window = parent_window

    def resizeEvent(self, event):
        """Actualizar preview cuando cambia el tamaño"""
        super().resizeEvent(event)
        if hasattr(self.parent_window, 'update_welcome_preview'):
            self.parent_window.update_welcome_preview()


class ConfigPhotoboothWindow(QMainWindow):
    """Ventana de configuración del photobooth"""

    # Señal cuando se guarda la configuración
    config_saved = Signal()

    def __init__(self, evento_id: int, parent=None):
        super().__init__(parent)

        self.evento_id = evento_id
        self.evento_nombre = ""
        self.config: Optional[PhotoboothConfig] = None

        # Cargar datos
        self.load_evento_data()

        self.init_ui()
        self.load_config()

    def load_evento_data(self):
        """Carga información del evento"""
        try:
            with get_session() as session:
                from sqlalchemy.orm import joinedload

                evento = session.query(Evento).options(
                    joinedload(Evento.cliente)
                ).filter(Evento.id == self.evento_id).first()

                if evento:
                    self.evento_nombre = evento.nombre

        except Exception as e:
            logger.error(f"Error cargando evento: {e}")

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle(f"Configuración Photobooth - {self.evento_nombre}")
        self.setMinimumSize(900, 700)

        # Widget central con scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.setCentralWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        main_layout = QVBoxLayout()
        container.setLayout(main_layout)

        # Título
        title = QLabel(f"Configuración del Photobooth")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        subtitle = QLabel(f"Evento: {self.evento_nombre}")
        subtitle.setStyleSheet("color: #666; font-size: 12px;")
        main_layout.addWidget(subtitle)

        # Tabs para organizar configuración
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Tab 1: Bienvenida
        tabs.addTab(self.create_welcome_tab(), "🎉 Bienvenida")

        # Tab 2: Cámara
        tabs.addTab(self.create_camera_tab(), "📷 Cámara")

        # Tab 3: Tiempos
        tabs.addTab(self.create_timing_tab(), "⏱ Tiempos")

        # Tab 4: Impresión
        tabs.addTab(self.create_printing_tab(), "🖨 Impresión")

        # Tab 5: Plantilla
        tabs.addTab(self.create_template_tab(), "🎨 Plantilla")

        # Botones
        buttons_layout = QHBoxLayout()

        self.btn_save = QPushButton("💾 Guardar Configuración")
        self.btn_save.clicked.connect(self.save_config)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        buttons_layout.addWidget(self.btn_save)

        self.btn_preview = QPushButton("👁 Vista Previa")
        self.btn_preview.clicked.connect(self.preview_config)
        buttons_layout.addWidget(self.btn_preview)

        self.btn_close = QPushButton("❌ Cerrar")
        self.btn_close.clicked.connect(self.close)
        buttons_layout.addWidget(self.btn_close)

        main_layout.addLayout(buttons_layout)

    def create_welcome_tab(self) -> QWidget:
        """Crea la pestaña de configuración de bienvenida"""
        widget = QWidget()
        main_layout = QHBoxLayout()  # Cambiar a horizontal para tener form + preview
        widget.setLayout(main_layout)

        # === Panel izquierdo: Controles ===
        left_panel = QWidget()
        layout = QVBoxLayout()
        left_panel.setLayout(layout)

        # Grupo de mensaje
        group = QGroupBox("Configuración")
        group_layout = QFormLayout()

        # Mensaje de bienvenida
        self.txt_mensaje = QLineEdit()
        self.txt_mensaje.setPlaceholderText("¡Bienvenido a nuestro evento!")
        self.txt_mensaje.textChanged.connect(self.update_welcome_preview)
        group_layout.addRow("Mensaje:", self.txt_mensaje)

        # Tamaño de texto
        self.spin_tamano_texto = QSpinBox()
        self.spin_tamano_texto.setRange(20, 100)
        self.spin_tamano_texto.setValue(48)
        self.spin_tamano_texto.setSuffix(" px")
        self.spin_tamano_texto.valueChanged.connect(self.update_welcome_preview)
        group_layout.addRow("Tamaño del texto:", self.spin_tamano_texto)

        # Color del texto
        color_layout = QHBoxLayout()
        self.btn_color_texto = QPushButton()
        self.btn_color_texto.setFixedSize(50, 30)
        self.btn_color_texto.setStyleSheet("background-color: #FFFFFF;")
        self.btn_color_texto.clicked.connect(self.choose_text_color)
        color_layout.addWidget(self.btn_color_texto)
        color_layout.addWidget(QLabel("(Haz click para cambiar)"))
        color_layout.addStretch()
        group_layout.addRow("Color del texto:", color_layout)

        # Imagen de fondo
        bg_layout = QHBoxLayout()
        self.btn_load_bg_image = QPushButton("Cargar Imagen")
        self.btn_load_bg_image.clicked.connect(self.load_background_image)
        bg_layout.addWidget(self.btn_load_bg_image)

        self.btn_remove_bg_image = QPushButton("Quitar")
        self.btn_remove_bg_image.clicked.connect(self.remove_background_image)
        bg_layout.addWidget(self.btn_remove_bg_image)

        self.lbl_bg_thumbnail = QLabel("Sin imagen")
        self.lbl_bg_thumbnail.setFixedSize(80, 60)
        self.lbl_bg_thumbnail.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        self.lbl_bg_thumbnail.setScaledContents(True)
        bg_layout.addWidget(self.lbl_bg_thumbnail)

        bg_layout.addStretch()
        group_layout.addRow("Imagen de fondo:", bg_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

        layout.addStretch()

        main_layout.addWidget(left_panel, 1)

        # === Panel derecho: Vista Previa ===
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        # Título del preview
        preview_title = QLabel("Vista Previa")
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_layout.addWidget(preview_title)

        # Frame del preview - contenedor principal con manejo de resize
        preview_frame = PreviewFrame(self)
        preview_frame.setMinimumSize(400, 300)
        preview_frame.setFixedHeight(300)
        preview_frame.setStyleSheet("border: 2px solid #ccc; border-radius: 5px; background-color: #f5f5f5;")

        # Label para la imagen de fondo (hijo directo del frame)
        self.lbl_background_preview = QLabel(preview_frame)
        self.lbl_background_preview.setGeometry(0, 0, 400, 300)
        self.lbl_background_preview.setScaledContents(False)
        self.lbl_background_preview.setAlignment(Qt.AlignCenter)
        self.lbl_background_preview.setStyleSheet("border: none; background-color: transparent;")

        # Label del mensaje (hijo directo del frame, encima del fondo)
        self.lbl_welcome_preview = QLabel("¡Bienvenido a nuestro evento!", preview_frame)
        self.lbl_welcome_preview.setGeometry(0, 0, 400, 300)
        self.lbl_welcome_preview.setAlignment(Qt.AlignCenter)
        self.lbl_welcome_preview.setWordWrap(True)
        self.lbl_welcome_preview.setStyleSheet("background-color: transparent; padding: 20px;")

        # Asegurar que el texto esté encima del fondo
        self.lbl_background_preview.lower()  # Enviar al fondo
        self.lbl_welcome_preview.raise_()    # Traer al frente

        right_layout.addWidget(preview_frame)

        # Info
        info = QLabel(
            "💡 La vista previa muestra cómo se verá el mensaje de bienvenida "
            "en la pantalla del photobooth."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-size: 11px; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        right_layout.addWidget(info)

        main_layout.addWidget(right_panel, 1)

        # Guardar referencia al frame para cambiar fondo
        self.welcome_preview_frame = preview_frame

        # Variable para la imagen de fondo
        self.background_image_path = None
        self.background_pixmap = None

        # Actualizar preview inicial
        self.update_welcome_preview()

        return widget

    def create_camera_tab(self) -> QWidget:
        """Crea la pestaña de configuración de cámara"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox("Configuración de Cámara")
        group_layout = QFormLayout()

        # Tipo de cámara
        self.combo_tipo_camara = QComboBox()
        self.combo_tipo_camara.addItems(["Webcam", "DSLR Nikon", "USB PTP"])
        group_layout.addRow("Tipo de cámara:", self.combo_tipo_camara)

        # Resolución
        self.combo_resolucion = QComboBox()
        self.combo_resolucion.addItems([
            "640x480",
            "1280x720",
            "1920x1080",
            "2560x1440",
            "3840x2160"
        ])
        self.combo_resolucion.setCurrentText("1280x720")
        group_layout.addRow("Resolución:", self.combo_resolucion)

        # Balance de blancos
        self.combo_balance_blancos = QComboBox()
        self.combo_balance_blancos.addItems([
            "auto",
            "daylight",
            "cloudy",
            "tungsten",
            "fluorescent"
        ])
        group_layout.addRow("Balance de blancos:", self.combo_balance_blancos)

        # ISO
        self.spin_iso = QSpinBox()
        self.spin_iso.setRange(100, 6400)
        self.spin_iso.setValue(400)
        self.spin_iso.setSingleStep(100)
        group_layout.addRow("ISO:", self.spin_iso)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Info
        info = QLabel(
            "💡 Nota: La configuración de balance de blancos e ISO solo aplica "
            "para cámaras DSLR compatibles."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(info)

        layout.addStretch()

        return widget

    def create_timing_tab(self) -> QWidget:
        """Crea la pestaña de configuración de tiempos"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox("Configuración de Tiempos")
        group_layout = QFormLayout()

        # Tiempo de cuenta regresiva
        self.spin_countdown = QSpinBox()
        self.spin_countdown.setRange(1, 10)
        self.spin_countdown.setValue(3)
        self.spin_countdown.setSuffix(" segundos")
        group_layout.addRow("Cuenta regresiva:", self.spin_countdown)

        # Tiempo entre fotos
        self.spin_between_photos = QSpinBox()
        self.spin_between_photos.setRange(1, 30)
        self.spin_between_photos.setValue(3)
        self.spin_between_photos.setSuffix(" segundos")
        group_layout.addRow("Entre fotos:", self.spin_between_photos)

        # Tiempo de visualización
        self.spin_preview_time = QSpinBox()
        self.spin_preview_time.setRange(1, 10)
        self.spin_preview_time.setValue(2)
        self.spin_preview_time.setSuffix(" segundos")
        group_layout.addRow("Visualización de foto:", self.spin_preview_time)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Descripción
        desc = QLabel(
            "• Cuenta regresiva: Tiempo antes de capturar cada foto (3, 2, 1, ¡Sonríe!)\n"
            "• Entre fotos: Tiempo de espera entre cada captura\n"
            "• Visualización: Tiempo que se muestra cada foto después de capturarla"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("padding: 10px; background: #e3f2fd; border-radius: 5px;")
        layout.addWidget(desc)

        layout.addStretch()

        return widget

    def create_printing_tab(self) -> QWidget:
        """Crea la pestaña de configuración de impresión"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox("Configuración de Impresión")
        group_layout = QFormLayout()

        # Impresora
        self.txt_printer = QLineEdit()
        self.txt_printer.setPlaceholderText("Nombre de la impresora")
        group_layout.addRow("Impresora:", self.txt_printer)

        # Tamaño de papel
        self.combo_paper_size = QComboBox()
        self.combo_paper_size.addItems([
            "10x15",
            "13x18",
            "15x21",
            "A4",
            "A5"
        ])
        group_layout.addRow("Tamaño de papel:", self.combo_paper_size)

        # Número de copias
        self.spin_copies = QSpinBox()
        self.spin_copies.setRange(1, 10)
        self.spin_copies.setValue(1)
        group_layout.addRow("Copias:", self.spin_copies)

        # Calidad
        self.combo_quality = QComboBox()
        self.combo_quality.addItems(["draft", "normal", "high", "best"])
        self.combo_quality.setCurrentText("high")
        group_layout.addRow("Calidad:", self.combo_quality)

        # Imprimir automáticamente
        self.check_auto_print = QCheckBox("Imprimir automáticamente al finalizar")
        group_layout.addRow("", self.check_auto_print)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Info
        info = QLabel(
            "⚠️ La funcionalidad de impresión está en desarrollo. "
            "Por ahora solo se guardan los ajustes."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #f57c00; padding: 10px; background: #fff3e0; border-radius: 5px;")
        layout.addWidget(info)

        layout.addStretch()

        return widget

    def create_template_tab(self) -> QWidget:
        """Crea la pestaña de selección de plantilla"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox("Plantilla de Collage")
        group_layout = QVBoxLayout()

        # Selector de plantilla
        form_layout = QFormLayout()

        self.combo_template = QComboBox()
        form_layout.addRow("Plantilla:", self.combo_template)

        # Botón para gestionar plantillas
        btn_manage_templates = QPushButton("⚙️ Gestionar Plantillas")
        btn_manage_templates.clicked.connect(self.open_template_manager)
        form_layout.addRow("", btn_manage_templates)

        group_layout.addLayout(form_layout)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # Info
        info = QLabel(
            "💡 Si no has creado plantillas, se usará una plantilla predeterminada "
            "de 4 fotos. Haz click en 'Gestionar Plantillas' para crear plantillas personalizadas."
        )
        info.setWordWrap(True)
        info.setStyleSheet("padding: 10px; background: #e8f5e9; border-radius: 5px;")
        layout.addWidget(info)

        layout.addStretch()

        return widget

    def load_config(self):
        """Carga la configuración existente"""
        try:
            with get_session() as session:
                config = session.query(PhotoboothConfig).filter(
                    PhotoboothConfig.evento_id == self.evento_id
                ).first()

                if config:
                    # Bienvenida
                    self.txt_mensaje.setText(config.mensaje_bienvenida or "")
                    self.spin_tamano_texto.setValue(config.tamano_texto or 48)

                    if config.color_texto:
                        color = QColor(config.color_texto)
                        self.btn_color_texto.setStyleSheet(f"background-color: {color.name()};")

                    # Cargar imagen de fondo si existe
                    if config.imagen_fondo:
                        absolute_path = get_absolute_path(config.imagen_fondo)
                        if absolute_path:
                            self.background_pixmap = QPixmap(str(absolute_path))
                            self.background_image_path = str(absolute_path)

                            # Actualizar thumbnail
                            thumbnail = self.background_pixmap.scaled(
                                80, 60,
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation
                            )
                            self.lbl_bg_thumbnail.setPixmap(thumbnail)
                        else:
                            logger.warning(f"Imagen de fondo no encontrada: {config.imagen_fondo}")

                    # Cámara
                    tipo_index = self.combo_tipo_camara.findText(config.tipo_camara or "Webcam")
                    if tipo_index >= 0:
                        self.combo_tipo_camara.setCurrentIndex(tipo_index)

                    self.combo_resolucion.setCurrentText(config.resolucion_camara or "1280x720")
                    self.combo_balance_blancos.setCurrentText(config.balance_blancos or "auto")
                    self.spin_iso.setValue(config.iso_valor or 400)

                    # Tiempos
                    self.spin_countdown.setValue(config.tiempo_cuenta_regresiva or 3)
                    self.spin_between_photos.setValue(config.tiempo_entre_fotos or 3)
                    self.spin_preview_time.setValue(config.tiempo_visualizacion_foto or 2)

                    # Impresión
                    self.txt_printer.setText(config.printer_name or "")
                    self.combo_paper_size.setCurrentText(config.paper_size or "10x15")
                    self.spin_copies.setValue(config.copias_impresion or 1)
                    self.combo_quality.setCurrentText(config.calidad_impresion or "high")
                    self.check_auto_print.setChecked(config.imprimir_automaticamente or False)

                # Cargar plantillas disponibles
                self.load_templates()

                if config and config.plantilla_collage_id:
                    # Seleccionar plantilla actual
                    for i in range(self.combo_template.count()):
                        if self.combo_template.itemData(i) == config.plantilla_collage_id:
                            self.combo_template.setCurrentIndex(i)
                            break

                # Actualizar preview inicial con los valores cargados
                self.update_welcome_preview()

        except Exception as e:
            logger.error(f"Error cargando configuración: {e}", exc_info=True)

    def load_templates(self):
        """Carga las plantillas disponibles para el evento"""
        try:
            self.combo_template.clear()
            self.combo_template.addItem("(Sin plantilla - usar predeterminada)", None)

            with get_session() as session:
                templates = session.query(CollageTemplate).filter(
                    CollageTemplate.evento_id == self.evento_id
                ).all()

                for template in templates:
                    label = template.nombre
                    if template.es_predeterminada:
                        label += " ⭐"

                    self.combo_template.addItem(label, template.template_id)

        except Exception as e:
            logger.error(f"Error cargando plantillas: {e}")

    def update_welcome_preview(self):
        """Actualiza la vista previa del mensaje de bienvenida en tiempo real"""
        # Verificar que los widgets existan
        if not hasattr(self, 'lbl_welcome_preview') or not hasattr(self, 'welcome_preview_frame'):
            return

        # Obtener valores actuales
        message = self.txt_mensaje.text() or "¡Bienvenido a nuestro evento!"
        size = self.spin_tamano_texto.value()
        color = self.btn_color_texto.palette().button().color().name()

        # Actualizar fuente y texto del preview
        font = QFont()
        font.setPointSize(size)
        font.setBold(True)
        self.lbl_welcome_preview.setFont(font)
        self.lbl_welcome_preview.setText(message)

        # Actualizar estilo del label de texto
        self.lbl_welcome_preview.setStyleSheet(f"color: {color}; padding: 20px; background-color: transparent;")

        # Actualizar fondo del frame si hay imagen
        if self.background_pixmap and hasattr(self, 'lbl_background_preview'):
            # Obtener el tamaño actual del frame
            frame_width = self.welcome_preview_frame.width()
            frame_height = self.welcome_preview_frame.height()

            # Verificar que el tamaño sea válido
            if frame_width <= 0 or frame_height <= 0:
                return

            # Escalar la imagen para que cubra todo el área (modo cover)
            pixmap_size = self.background_pixmap.size()
            scale_x = frame_width / pixmap_size.width()
            scale_y = frame_height / pixmap_size.height()
            scale = max(scale_x, scale_y)  # Usar la escala mayor para cubrir

            # Calcular nuevo tamaño
            new_width = int(pixmap_size.width() * scale)
            new_height = int(pixmap_size.height() * scale)

            # Escalar el pixmap
            scaled_pixmap = self.background_pixmap.scaled(
                new_width,
                new_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            # Centrar la imagen recortando si es necesario
            if new_width > frame_width or new_height > frame_height:
                x_offset = (new_width - frame_width) // 2
                y_offset = (new_height - frame_height) // 2
                scaled_pixmap = scaled_pixmap.copy(x_offset, y_offset, frame_width, frame_height)

            # Aplicar el pixmap al label de fondo
            self.lbl_background_preview.setPixmap(scaled_pixmap)
            self.lbl_background_preview.setScaledContents(False)

            # Actualizar geometría de los labels
            self.lbl_background_preview.setGeometry(0, 0, frame_width, frame_height)
            self.lbl_welcome_preview.setGeometry(0, 0, frame_width, frame_height)

            # Asegurar Z-order
            self.lbl_background_preview.lower()
            self.lbl_welcome_preview.raise_()
        else:
            # Sin imagen de fondo, limpiar el label
            self.lbl_background_preview.clear()

    def choose_text_color(self):
        """Abre el selector de color para el texto"""
        current_color = self.btn_color_texto.palette().button().color()
        color = QColorDialog.getColor(current_color, self, "Seleccionar Color del Texto")

        if color.isValid():
            self.btn_color_texto.setStyleSheet(f"background-color: {color.name()};")
            self.update_welcome_preview()  # Actualizar preview

    def load_background_image(self):
        """Carga una imagen de fondo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen de Fondo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            # Cargar la imagen
            self.background_pixmap = QPixmap(file_path)
            self.background_image_path = file_path

            # Actualizar thumbnail
            thumbnail = self.background_pixmap.scaled(
                80, 60,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.lbl_bg_thumbnail.setPixmap(thumbnail)

            # Actualizar preview
            self.update_welcome_preview()

    def remove_background_image(self):
        """Quita la imagen de fondo"""
        self.background_pixmap = None
        self.background_image_path = None
        self.lbl_bg_thumbnail.clear()
        self.lbl_bg_thumbnail.setText("Sin imagen")

        # Actualizar preview
        self.update_welcome_preview()

    def save_config(self):
        """Guarda la configuración"""
        try:
            # Copiar imagen de fondo si existe y aún no está en media/backgrounds
            saved_image_path = None
            if self.background_image_path:
                try:
                    from pathlib import Path
                    # Verificar si la imagen ya está en media/backgrounds
                    if "media\\backgrounds" in self.background_image_path or "media/backgrounds" in self.background_image_path:
                        # Ya está guardada, usar ruta tal cual
                        saved_image_path = self.background_image_path
                    else:
                        # Copiar a media/backgrounds
                        saved_image_path = copy_background_image(self.background_image_path)
                        logger.info(f"Imagen de bienvenida copiada: {saved_image_path}")
                except Exception as e:
                    logger.error(f"Error copiando imagen de fondo: {e}")
                    QMessageBox.warning(
                        self,
                        "Advertencia",
                        f"No se pudo copiar la imagen de fondo: {str(e)}\nLa configuración se guardará sin imagen."
                    )

            with get_session() as session:
                config = session.query(PhotoboothConfig).filter(
                    PhotoboothConfig.evento_id == self.evento_id
                ).first()

                if not config:
                    config = PhotoboothConfig(evento_id=self.evento_id)
                    session.add(config)

                # Guardar valores
                config.mensaje_bienvenida = self.txt_mensaje.text()
                config.tamano_texto = self.spin_tamano_texto.value()
                config.color_texto = self.btn_color_texto.palette().button().color().name()
                config.imagen_fondo = saved_image_path  # Guardar ruta relativa de imagen de fondo

                config.tipo_camara = self.combo_tipo_camara.currentText()
                config.resolucion_camara = self.combo_resolucion.currentText()
                config.balance_blancos = self.combo_balance_blancos.currentText()
                config.iso_valor = self.spin_iso.value()

                config.tiempo_cuenta_regresiva = self.spin_countdown.value()
                config.tiempo_entre_fotos = self.spin_between_photos.value()
                config.tiempo_visualizacion_foto = self.spin_preview_time.value()

                config.printer_name = self.txt_printer.text()
                config.paper_size = self.combo_paper_size.currentText()
                config.copias_impresion = self.spin_copies.value()
                config.calidad_impresion = self.combo_quality.currentText()
                config.imprimir_automaticamente = self.check_auto_print.isChecked()

                # Plantilla seleccionada
                template_id = self.combo_template.currentData()
                config.plantilla_collage_id = template_id

                session.commit()

                QMessageBox.information(
                    self,
                    "Éxito",
                    "Configuración guardada correctamente"
                )

                self.config_saved.emit()

        except Exception as e:
            logger.error(f"Error guardando configuración: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error guardando configuración: {str(e)}")

    def preview_config(self):
        """Muestra una vista previa de la configuración"""
        QMessageBox.information(
            self,
            "Vista Previa",
            "La funcionalidad de vista previa estará disponible próximamente"
        )

    def open_template_manager(self):
        """Abre el gestor de plantillas"""
        try:
            from ..collage_editor import TemplateListWindow

            templates_window = TemplateListWindow(self.evento_id, self)
            templates_window.show()

            # Recargar plantillas cuando se cierre
            templates_window.destroyed.connect(self.load_templates)

        except Exception as e:
            logger.error(f"Error abriendo gestor de plantillas: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
