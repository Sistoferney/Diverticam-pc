"""
Ventana para listar y gestionar plantillas de collage
"""
import logging
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from database import get_session, CollageTemplate, PhotoboothConfig
from .template_editor_window import TemplateEditorWindow

logger = logging.getLogger(__name__)


class TemplateListWindow(QMainWindow):
    """Ventana para listar plantillas de collage"""

    # Señal cuando se selecciona una plantilla
    template_selected = Signal(str)  # template_id

    def __init__(self, evento_id: int, parent=None):
        super().__init__(parent)

        self.evento_id = evento_id
        self.evento_nombre = ""

        # Cargar nombre del evento
        self.load_evento_info()

        self.init_ui()
        self.load_templates()

    def load_evento_info(self):
        """Carga información básica del evento"""
        try:
            with get_session() as session:
                from database import Evento
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
        self.setWindowTitle(f"Plantillas de Collage - {self.evento_nombre}")
        self.setMinimumSize(800, 600)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Título
        title = QLabel(f"Plantillas de Collage - {self.evento_nombre}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Instrucciones
        instructions = QLabel(
            "Aquí puedes ver, editar y gestionar las plantillas de collage para este evento.\n"
            "Marca una plantilla como predeterminada para usarla automáticamente en el photobooth."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #e3f2fd; border-radius: 5px;")
        layout.addWidget(instructions)

        # Botones superiores
        top_buttons = QHBoxLayout()

        self.btn_new = QPushButton("+ Nueva Plantilla")
        self.btn_new.clicked.connect(self.new_template)
        top_buttons.addWidget(self.btn_new)

        self.btn_edit = QPushButton("✏️ Editar")
        self.btn_edit.clicked.connect(self.edit_template)
        self.btn_edit.setEnabled(False)
        top_buttons.addWidget(self.btn_edit)

        self.btn_set_default = QPushButton("⭐ Marcar como Predeterminada")
        self.btn_set_default.clicked.connect(self.set_default_template)
        self.btn_set_default.setEnabled(False)
        top_buttons.addWidget(self.btn_set_default)

        self.btn_delete = QPushButton("🗑 Eliminar")
        self.btn_delete.clicked.connect(self.delete_template)
        self.btn_delete.setEnabled(False)
        top_buttons.addWidget(self.btn_delete)

        top_buttons.addStretch()

        self.btn_refresh = QPushButton("🔄 Refrescar")
        self.btn_refresh.clicked.connect(self.load_templates)
        top_buttons.addWidget(self.btn_refresh)

        layout.addLayout(top_buttons)

        # Tabla de plantillas
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Descripción", "Fotos", "Predeterminada"
        ])

        # Configurar tabla
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Ocultar columna ID
        self.table.setColumnHidden(0, True)

        # Eventos
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        self.table.itemDoubleClicked.connect(self.edit_template)

        layout.addWidget(self.table)

        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

    def load_templates(self):
        """Carga las plantillas del evento"""
        try:
            with get_session() as session:
                templates = session.query(CollageTemplate).filter(
                    CollageTemplate.evento_id == self.evento_id
                ).order_by(CollageTemplate.created_at.desc()).all()

                self.table.setRowCount(0)

                for template in templates:
                    row = self.table.rowCount()
                    self.table.insertRow(row)

                    # ID (oculto)
                    self.table.setItem(row, 0, QTableWidgetItem(template.template_id))

                    # Nombre
                    self.table.setItem(row, 1, QTableWidgetItem(template.nombre))

                    # Descripción
                    desc = template.descripcion or ""
                    self.table.setItem(row, 2, QTableWidgetItem(desc[:100]))

                    # Número de fotos
                    import json
                    template_data = template.template_data
                    if isinstance(template_data, str):
                        template_data = json.loads(template_data)

                    num_photos = template_data.get('num_photos', 0)
                    self.table.setItem(row, 3, QTableWidgetItem(str(num_photos)))

                    # Predeterminada
                    default_text = "✓ Sí" if template.es_predeterminada else ""
                    item = QTableWidgetItem(default_text)
                    if template.es_predeterminada:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    self.table.setItem(row, 4, item)

                # Ajustar columnas
                self.table.resizeColumnsToContents()

                logger.info(f"Cargadas {len(templates)} plantillas")

        except Exception as e:
            logger.error(f"Error cargando plantillas: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error cargando plantillas: {str(e)}")

    def on_selection_changed(self):
        """Maneja el cambio de selección"""
        has_selection = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has_selection)
        self.btn_set_default.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def new_template(self):
        """Crea una nueva plantilla"""
        try:
            editor = TemplateEditorWindow(self.evento_id, parent=self)
            editor.template_saved.connect(self.on_template_saved)
            editor.show()
        except Exception as e:
            logger.error(f"Error abriendo editor: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error abriendo editor: {str(e)}")

    def edit_template(self):
        """Edita la plantilla seleccionada"""
        selected = self.table.selectedIndexes()
        if not selected:
            return

        row = selected[0].row()
        template_id = self.table.item(row, 0).text()

        try:
            editor = TemplateEditorWindow(self.evento_id, template_id, parent=self)
            editor.template_saved.connect(self.on_template_saved)
            editor.show()
        except Exception as e:
            logger.error(f"Error abriendo editor: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error abriendo editor: {str(e)}")

    def set_default_template(self):
        """Marca la plantilla seleccionada como predeterminada"""
        selected = self.table.selectedIndexes()
        if not selected:
            return

        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        template_name = self.table.item(row, 1).text()

        try:
            with get_session() as session:
                # Desmarcar todas las plantillas predeterminadas del evento
                templates = session.query(CollageTemplate).filter(
                    CollageTemplate.evento_id == self.evento_id
                ).all()

                for template in templates:
                    template.es_predeterminada = False

                # Marcar la seleccionada como predeterminada
                template = session.query(CollageTemplate).filter(
                    CollageTemplate.template_id == template_id
                ).first()

                if template:
                    template.es_predeterminada = True

                    # Actualizar la configuración del photobooth para usar esta plantilla
                    config = session.query(PhotoboothConfig).filter(
                        PhotoboothConfig.evento_id == self.evento_id
                    ).first()

                    if config:
                        config.plantilla_collage_id = template_id

                    session.commit()

                    QMessageBox.information(
                        self,
                        "Éxito",
                        f"La plantilla '{template_name}' ahora es la predeterminada"
                    )

                    self.load_templates()

        except Exception as e:
            logger.error(f"Error marcando plantilla como predeterminada: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def delete_template(self):
        """Elimina la plantilla seleccionada"""
        selected = self.table.selectedIndexes()
        if not selected:
            return

        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        template_name = self.table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar la plantilla '{template_name}'?\n\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                with get_session() as session:
                    template = session.query(CollageTemplate).filter(
                        CollageTemplate.template_id == template_id
                    ).first()

                    if template:
                        session.delete(template)
                        session.commit()

                        QMessageBox.information(self, "Éxito", "Plantilla eliminada correctamente")
                        self.load_templates()

            except Exception as e:
                logger.error(f"Error eliminando plantilla: {e}", exc_info=True)
                QMessageBox.critical(self, "Error", f"Error eliminando plantilla: {str(e)}")

    def on_template_saved(self, template_id: str):
        """Se llama cuando se guarda una plantilla"""
        self.load_templates()
