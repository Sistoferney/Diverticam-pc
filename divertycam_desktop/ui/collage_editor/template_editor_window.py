"""
Ventana del editor de plantillas de collage
"""
import logging
import json
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
    QColorDialog, QFileDialog, QGroupBox, QMessageBox, QScrollArea, QSlider
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QFont

import config
from database import get_session, Evento, CollageTemplate
from .collage_canvas import CollageCanvas, CollageCanvasView
from .photo_frame_item import PhotoFrameItem

logger = logging.getLogger(__name__)


class TemplateEditorWindow(QMainWindow):
    """Ventana del editor de plantillas de collage"""

    # Señal cuando se guarda la plantilla
    template_saved = Signal(str)  # template_id

    def __init__(self, evento_id: int, template_id: Optional[str] = None, parent=None):
        super().__init__(parent)

        self.evento_id = evento_id
        self.template_id = template_id
        self.evento: Optional[Evento] = None

        # Cargar información del evento
        if not self.load_evento():
            QMessageBox.critical(self, "Error", "No se pudo cargar el evento")
            self.close()
            return

        # Obtener aspect ratio de la configuración de cámara
        self.aspect_ratio = self.get_camera_aspect_ratio()

        self.init_ui()
        self.init_canvas()

        # Cargar plantilla si se especificó un ID
        if template_id:
            self.load_template(template_id)

    def load_evento(self) -> bool:
        """Carga información del evento"""
        try:
            with get_session() as session:
                self.evento = session.query(Evento).filter(Evento.id == self.evento_id).first()
                return self.evento is not None
        except Exception as e:
            logger.error(f"Error cargando evento: {e}")
            return False

    def get_camera_aspect_ratio(self) -> float:
        """Obtiene la relación de aspecto de la cámara configurada"""
        try:
            with get_session() as session:
                from database import PhotoboothConfig
                config_db = session.query(PhotoboothConfig).filter(
                    PhotoboothConfig.evento_id == self.evento_id
                ).first()

                if config_db and config_db.resolucion_camara:
                    # Parsear resolución (ej: "1280x720")
                    parts = config_db.resolucion_camara.split('x')
                    if len(parts) == 2:
                        width = int(parts[0])
                        height = int(parts[1])
                        return width / height
        except Exception as e:
            logger.error(f"Error obteniendo aspect ratio: {e}")

        # Por defecto 16:9
        return 16 / 9

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"Editor de Plantillas - {self.evento.nombre}")
        self.setMinimumSize(1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # === Panel izquierdo: Canvas ===
        canvas_layout = QVBoxLayout()

        # Título
        title_label = QLabel(f"Editor de Plantillas - {self.evento.nombre}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        canvas_layout.addWidget(title_label)

        # Info del evento
        info_label = QLabel(f"Cliente: {self.evento.cliente.nombre_completo}")
        canvas_layout.addWidget(info_label)

        # Instrucciones
        instructions = QLabel(
            "Diseña tu collage personalizado. Añade marcos de fotos y posiciónalos libremente.\n"
            "Los marcos mantienen automáticamente la relación de aspecto de la cámara configurada."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        canvas_layout.addWidget(instructions)

        # Placeholder para el canvas (se creará después)
        self.canvas_view = None  # Se inicializa en init_canvas()
        canvas_layout.addWidget(QLabel("Cargando canvas..."))  # Temporal

        # Botones bajo el canvas
        canvas_buttons = QHBoxLayout()

        self.btn_add_frame = QPushButton("Añadir Marco")
        self.btn_add_frame.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        self.btn_add_frame.clicked.connect(self.add_frame)
        canvas_buttons.addWidget(self.btn_add_frame)

        self.btn_clear = QPushButton("Limpiar Todo")
        self.btn_clear.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.btn_clear.clicked.connect(self.clear_canvas)
        canvas_buttons.addWidget(self.btn_clear)

        self.btn_save = QPushButton("Guardar Plantilla")
        self.btn_save.setIcon(self.style().standardIcon(self.style().SP_DialogSaveButton))
        self.btn_save.clicked.connect(self.save_template)
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        canvas_buttons.addWidget(self.btn_save)

        canvas_layout.addLayout(canvas_buttons)

        main_layout.addLayout(canvas_layout, 2)  # 2 partes de 3

        # === Panel derecho: Herramientas ===
        tools_widget = QWidget()
        tools_widget.setMaximumWidth(350)
        tools_widget.setStyleSheet("""
            QWidget {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
        """)

        tools_layout = QVBoxLayout()
        tools_widget.setLayout(tools_layout)

        # Scroll area para las herramientas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(tools_widget)
        main_layout.addWidget(scroll, 1)  # 1 parte de 3

        # Crear secciones de herramientas
        self.create_details_section(tools_layout)
        self.create_background_section(tools_layout)
        self.create_frame_properties_section(tools_layout)
        self.create_actions_section(tools_layout)

        # Stretch al final
        tools_layout.addStretch()

    def init_canvas(self):
        """Inicializa el canvas de collage"""
        # Crear canvas
        self.canvas = CollageCanvas(
            width_cm=15,
            height_cm=10,
            aspect_ratio=self.aspect_ratio
        )

        # Conectar señales
        self.canvas.frame_selected.connect(self.on_frame_selected)
        self.canvas.frame_deselected.connect(self.on_frame_deselected)

        # Crear vista
        self.canvas_view = CollageCanvasView(self.canvas)
        self.canvas_view.setMinimumSize(600, 400)

        # Reemplazar el label temporal con el canvas
        central_widget = self.centralWidget()
        layout = central_widget.layout()
        canvas_container = layout.itemAt(0).layout()  # Primera columna

        # Remover el label temporal (último item antes de los botones)
        item = canvas_container.itemAt(3)
        if item:
            widget = item.widget()
            if widget:
                canvas_container.removeWidget(widget)
                widget.deleteLater()

        # Agregar canvas view
        canvas_container.insertWidget(3, self.canvas_view)

    def create_details_section(self, parent_layout):
        """Crea la sección de detalles de la plantilla"""
        group = QGroupBox("Detalles de la Plantilla")
        layout = QVBoxLayout()

        # Nombre
        layout.addWidget(QLabel("Nombre:"))
        self.txt_name = QLineEdit("Mi collage personalizado")
        layout.addWidget(self.txt_name)

        # Descripción
        layout.addWidget(QLabel("Descripción:"))
        self.txt_description = QTextEdit()
        self.txt_description.setMaximumHeight(80)
        layout.addWidget(self.txt_description)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_background_section(self, parent_layout):
        """Crea la sección de configuración de fondo"""
        group = QGroupBox("Fondo")
        layout = QVBoxLayout()

        # Color de fondo
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.btn_bg_color = QPushButton()
        self.btn_bg_color.setFixedSize(40, 30)
        self.btn_bg_color.setStyleSheet("background-color: white;")
        self.btn_bg_color.clicked.connect(self.choose_background_color)
        color_layout.addWidget(self.btn_bg_color)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # Imagen de fondo
        layout.addWidget(QLabel("Imagen de fondo:"))
        bg_image_layout = QHBoxLayout()
        self.btn_load_bg = QPushButton("Cargar Imagen")
        self.btn_load_bg.clicked.connect(self.load_background_image)
        bg_image_layout.addWidget(self.btn_load_bg)

        self.btn_remove_bg = QPushButton("Quitar")
        self.btn_remove_bg.clicked.connect(self.remove_background_image)
        bg_image_layout.addWidget(self.btn_remove_bg)
        layout.addLayout(bg_image_layout)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_frame_properties_section(self, parent_layout):
        """Crea la sección de propiedades del marco seleccionado"""
        self.frame_props_group = QGroupBox("Marco Seleccionado")
        layout = QVBoxLayout()

        # Información cuando no hay marco seleccionado
        self.no_selection_label = QLabel("Ningún marco seleccionado\n\nHaz clic en un marco para editarlo")
        self.no_selection_label.setAlignment(Qt.AlignCenter)
        self.no_selection_label.setStyleSheet("color: #999; padding: 20px;")
        layout.addWidget(self.no_selection_label)

        # Propiedades (inicialmente ocultas)
        self.frame_props_widget = QWidget()
        props_layout = QVBoxLayout()

        # Ancho
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Ancho (mm):"))
        self.spin_frame_width = QSpinBox()
        self.spin_frame_width.setRange(10, 200)
        self.spin_frame_width.setValue(40)
        self.spin_frame_width.valueChanged.connect(self.on_frame_width_changed)
        width_layout.addWidget(self.spin_frame_width)
        props_layout.addLayout(width_layout)

        # Alto
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Alto (mm):"))
        self.spin_frame_height = QSpinBox()
        self.spin_frame_height.setRange(10, 200)
        self.spin_frame_height.setValue(40)
        self.spin_frame_height.valueChanged.connect(self.on_frame_height_changed)
        height_layout.addWidget(self.spin_frame_height)
        props_layout.addLayout(height_layout)

        # Info de aspect ratio
        info = QLabel(f"Los marcos mantienen la relación {self.aspect_ratio:.2f}:1")
        info.setWordWrap(True)
        info.setStyleSheet("font-size: 10px; color: #666; padding: 5px;")
        props_layout.addWidget(info)

        # Botón eliminar
        self.btn_delete_frame = QPushButton("Eliminar Marco")
        self.btn_delete_frame.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.btn_delete_frame.clicked.connect(self.delete_selected_frame)
        props_layout.addWidget(self.btn_delete_frame)

        self.frame_props_widget.setLayout(props_layout)
        self.frame_props_widget.setVisible(False)
        layout.addWidget(self.frame_props_widget)

        self.frame_props_group.setLayout(layout)
        parent_layout.addWidget(self.frame_props_group)

    def create_actions_section(self, parent_layout):
        """Crea la sección de acciones"""
        group = QGroupBox("Acciones")
        layout = QVBoxLayout()

        self.btn_close = QPushButton("Cerrar Editor")
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def add_frame(self):
        """Agrega un nuevo marco al canvas"""
        self.canvas.add_frame(width=100)

    def clear_canvas(self):
        """Limpia todos los marcos del canvas"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Está seguro de que desea eliminar todos los marcos?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.canvas.clear_all_frames()

    def choose_background_color(self):
        """Abre el selector de color para el fondo"""
        color = QColorDialog.getColor(self.canvas.background_color, self, "Seleccionar Color de Fondo")

        if color.isValid():
            self.canvas.set_background_color(color)
            self.btn_bg_color.setStyleSheet(f"background-color: {color.name()};")

    def load_background_image(self):
        """Carga una imagen de fondo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen de Fondo",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.canvas.set_background_image(file_path)

    def remove_background_image(self):
        """Quita la imagen de fondo"""
        self.canvas.remove_background_image()

    def on_frame_selected(self, frame: PhotoFrameItem):
        """Maneja la selección de un marco"""
        self.no_selection_label.setVisible(False)
        self.frame_props_widget.setVisible(True)

        # Actualizar valores
        rect = frame.rect()
        cm_to_pixel = self.canvas.cm_to_pixel

        width_mm = int(rect.width() / cm_to_pixel * 10)
        height_mm = int(rect.height() / cm_to_pixel * 10)

        self.spin_frame_width.blockSignals(True)
        self.spin_frame_height.blockSignals(True)

        self.spin_frame_width.setValue(width_mm)
        self.spin_frame_height.setValue(height_mm)

        self.spin_frame_width.blockSignals(False)
        self.spin_frame_height.blockSignals(False)

    def on_frame_deselected(self):
        """Maneja la deselección de marcos"""
        self.no_selection_label.setVisible(True)
        self.frame_props_widget.setVisible(False)

    def on_frame_width_changed(self, value):
        """Maneja cambio de ancho del marco"""
        if self.canvas.selected_frame:
            cm_to_pixel = self.canvas.cm_to_pixel
            width_px = (value / 10) * cm_to_pixel
            height_px = width_px / self.aspect_ratio

            self.canvas.selected_frame.setRect(0, 0, width_px, height_px)
            self.canvas.selected_frame.update_handles_position()

            # Actualizar altura
            self.spin_frame_height.blockSignals(True)
            self.spin_frame_height.setValue(int(height_px / cm_to_pixel * 10))
            self.spin_frame_height.blockSignals(False)

    def on_frame_height_changed(self, value):
        """Maneja cambio de alto del marco"""
        if self.canvas.selected_frame:
            cm_to_pixel = self.canvas.cm_to_pixel
            height_px = (value / 10) * cm_to_pixel
            width_px = height_px * self.aspect_ratio

            self.canvas.selected_frame.setRect(0, 0, width_px, height_px)
            self.canvas.selected_frame.update_handles_position()

            # Actualizar ancho
            self.spin_frame_width.blockSignals(True)
            self.spin_frame_width.setValue(int(width_px / cm_to_pixel * 10))
            self.spin_frame_width.blockSignals(False)

    def delete_selected_frame(self):
        """Elimina el marco seleccionado"""
        self.canvas.delete_selected_frame()

    def save_template(self):
        """Guarda la plantilla en la base de datos"""
        try:
            # Validar nombre
            name = self.txt_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Por favor ingrese un nombre para la plantilla")
                return

            # Validar que haya al menos un marco
            if len(self.canvas.frames) == 0:
                QMessageBox.warning(self, "Error", "Agregue al menos un marco a la plantilla")
                return

            # Obtener datos de la plantilla
            template_data = self.canvas.get_template_data()
            template_data['nombre'] = name
            template_data['descripcion'] = self.txt_description.toPlainText()

            # Guardar en base de datos
            import uuid
            with get_session() as session:
                if self.template_id:
                    # Actualizar plantilla existente
                    template = session.query(CollageTemplate).filter(
                        CollageTemplate.template_id == self.template_id
                    ).first()

                    if template:
                        template.nombre = name
                        template.descripcion = self.txt_description.toPlainText()
                        template.background_color = self.canvas.background_color.name()
                        template.template_data = json.dumps(template_data)
                else:
                    # Crear nueva plantilla
                    template_id = str(uuid.uuid4())
                    template = CollageTemplate(
                        template_id=template_id,
                        nombre=name,
                        descripcion=self.txt_description.toPlainText(),
                        background_color=self.canvas.background_color.name(),
                        template_data=json.dumps(template_data),
                        evento_id=self.evento_id,
                        es_predeterminada=False
                    )
                    session.add(template)
                    self.template_id = template_id

                session.commit()

                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Plantilla '{name}' guardada correctamente"
                )

                # Emitir señal
                self.template_saved.emit(self.template_id)

                logger.info(f"Plantilla guardada: {self.template_id}")

        except Exception as e:
            logger.error(f"Error guardando plantilla: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al guardar la plantilla: {str(e)}")

    def load_template(self, template_id: str):
        """Carga una plantilla existente"""
        try:
            with get_session() as session:
                template = session.query(CollageTemplate).filter(
                    CollageTemplate.template_id == template_id
                ).first()

                if not template:
                    logger.error(f"Plantilla no encontrada: {template_id}")
                    return

                # Cargar datos en la interfaz
                self.txt_name.setText(template.nombre)
                self.txt_description.setPlainText(template.descripcion or "")

                # Cargar color de fondo
                color = QColor(template.background_color)
                self.canvas.set_background_color(color)
                self.btn_bg_color.setStyleSheet(f"background-color: {color.name()};")

                # Cargar template_data
                template_data = template.template_data
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)

                self.canvas.load_template_data(template_data)

                logger.info(f"Plantilla cargada: {template_id}")

        except Exception as e:
            logger.error(f"Error cargando plantilla: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error al cargar la plantilla: {str(e)}")
