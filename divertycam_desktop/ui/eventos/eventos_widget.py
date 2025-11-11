"""
Widget de gestión de eventos
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

from database import get_session, Evento
from .evento_dialog import EventoDialog
from ..photobooth import PhotoboothWindow
from ..collage_editor import TemplateListWindow

logger = logging.getLogger(__name__)


class EventosWidget(QWidget):
    """Widget principal para gestión de eventos"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_eventos()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()

        # Barra de herramientas superior
        toolbar = QHBoxLayout()

        # Botón Nuevo
        self.btn_nuevo = QPushButton("Nuevo Evento")
        self.btn_nuevo.clicked.connect(self.nuevo_evento)
        toolbar.addWidget(self.btn_nuevo)

        # Botón Editar
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_evento)
        self.btn_editar.setEnabled(False)
        toolbar.addWidget(self.btn_editar)

        # Botón Eliminar
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_evento)
        self.btn_eliminar.setEnabled(False)
        toolbar.addWidget(self.btn_eliminar)

        # Separador
        toolbar.addSpacing(20)

        # Botón Editor de Plantillas
        self.btn_editor = QPushButton("Editor de Plantillas")
        self.btn_editor.clicked.connect(self.abrir_editor_plantillas)
        self.btn_editor.setEnabled(False)
        toolbar.addWidget(self.btn_editor)

        # Botón Photobooth
        self.btn_photobooth = QPushButton("Iniciar Photobooth")
        self.btn_photobooth.clicked.connect(self.iniciar_photobooth)
        self.btn_photobooth.setEnabled(False)
        toolbar.addWidget(self.btn_photobooth)

        toolbar.addStretch()

        # Barra de búsqueda
        search_label = QLabel("Buscar:")
        toolbar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nombre, cliente, dirección...")
        self.search_input.textChanged.connect(self.filtrar_eventos)
        toolbar.addWidget(self.search_input)

        # Botón Refrescar
        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self.cargar_eventos)
        toolbar.addWidget(self.btn_refrescar)

        layout.addLayout(toolbar)

        # Tabla de eventos
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Fecha/Hora", "Cliente", "Dirección"
        ])

        # Configurar tabla
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Ocultar columna ID
        self.tabla.setColumnHidden(0, True)

        # Eventos de tabla
        self.tabla.itemSelectionChanged.connect(self.on_selection_changed)
        self.tabla.itemDoubleClicked.connect(self.editar_evento)

        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def cargar_eventos(self):
        """Carga todos los eventos de la base de datos"""
        try:
            with get_session() as session:
                eventos = session.query(Evento).order_by(Evento.fecha_hora.desc()).all()

                self.tabla.setRowCount(0)  # Limpiar tabla

                for evento in eventos:
                    self.agregar_evento_a_tabla(evento)

            logger.info(f"Cargados {len(eventos)} eventos")

        except Exception as e:
            logger.error(f"Error al cargar eventos: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar eventos: {str(e)}")

    def agregar_evento_a_tabla(self, evento: Evento):
        """Agrega un evento a la tabla"""
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)

        self.tabla.setItem(row, 0, QTableWidgetItem(str(evento.id)))
        self.tabla.setItem(row, 1, QTableWidgetItem(evento.nombre))
        self.tabla.setItem(row, 2, QTableWidgetItem(
            evento.fecha_hora.strftime('%d/%m/%Y %H:%M') if evento.fecha_hora else ""
        ))
        self.tabla.setItem(row, 3, QTableWidgetItem(evento.cliente.nombre_completo if evento.cliente else ""))
        self.tabla.setItem(row, 4, QTableWidgetItem(evento.direccion))

    def filtrar_eventos(self, texto):
        """Filtra los eventos en la tabla según el texto de búsqueda"""
        for row in range(self.tabla.rowCount()):
            mostrar = False

            # Buscar en cada columna (excepto ID)
            for col in range(1, self.tabla.columnCount()):
                item = self.tabla.item(row, col)
                if item and texto.lower() in item.text().lower():
                    mostrar = True
                    break

            self.tabla.setRowHidden(row, not mostrar)

    def on_selection_changed(self):
        """Maneja el cambio de selección en la tabla"""
        hay_seleccion = len(self.tabla.selectedItems()) > 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)
        self.btn_editor.setEnabled(hay_seleccion)
        self.btn_photobooth.setEnabled(hay_seleccion)

    def nuevo_evento(self):
        """Abre el diálogo para crear un nuevo evento"""
        dialog = EventoDialog(self)

        if dialog.exec():
            self.cargar_eventos()

    def editar_evento(self):
        """Abre el diálogo para editar el evento seleccionado"""
        selected_rows = self.tabla.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        evento_id = int(self.tabla.item(row, 0).text())

        try:
            with get_session() as session:
                evento = session.query(Evento).filter(Evento.id == evento_id).first()

                if evento:
                    dialog = EventoDialog(self, evento)

                    if dialog.exec():
                        self.cargar_eventos()
                else:
                    QMessageBox.warning(self, "Aviso", "Evento no encontrado")

        except Exception as e:
            logger.error(f"Error al editar evento: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar evento: {str(e)}")

    def eliminar_evento(self):
        """Elimina el evento seleccionado"""
        selected_rows = self.tabla.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        evento_id = int(self.tabla.item(row, 0).text())
        nombre = self.tabla.item(row, 1).text()

        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar el evento '{nombre}'?\n\n"
            "Esta acción también eliminará toda la configuración de photobooth asociada.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                with get_session() as session:
                    evento = session.query(Evento).filter(Evento.id == evento_id).first()

                    if evento:
                        session.delete(evento)
                        session.commit()

                        QMessageBox.information(self, "Éxito", "Evento eliminado correctamente")
                        self.cargar_eventos()
                    else:
                        QMessageBox.warning(self, "Aviso", "Evento no encontrado")

            except Exception as e:
                logger.error(f"Error al eliminar evento: {e}")
                QMessageBox.critical(self, "Error", f"Error al eliminar evento: {str(e)}")

    def iniciar_photobooth(self):
        """Inicia el photobooth para el evento seleccionado"""
        selected_rows = self.tabla.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Por favor seleccione un evento")
            return

        row = selected_rows[0].row()
        evento_id = int(self.tabla.item(row, 0).text())
        evento_nombre = self.tabla.item(row, 1).text()

        try:
            # Verificar que el evento tenga configuración de photobooth
            with get_session() as session:
                evento = session.query(Evento).filter(Evento.id == evento_id).first()

                if not evento:
                    QMessageBox.warning(self, "Error", "Evento no encontrado")
                    return

                if not evento.photobooth_config:
                    reply = QMessageBox.question(
                        self,
                        "Configuración requerida",
                        f"El evento '{evento_nombre}' no tiene configuración de photobooth.\n\n"
                        "¿Desea crear una configuración básica ahora?",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        from database.models import PhotoboothConfig
                        config = PhotoboothConfig(evento_id=evento_id)
                        session.add(config)
                        session.commit()
                        logger.info(f"Configuración de photobooth creada para evento {evento_id}")
                    else:
                        return

            # Abrir ventana de photobooth
            self.photobooth_window = PhotoboothWindow(evento_id, self)
            self.photobooth_window.show()

            logger.info(f"Photobooth iniciado para evento: {evento_nombre}")

        except Exception as e:
            logger.error(f"Error iniciando photobooth: {e}")
            QMessageBox.critical(self, "Error", f"Error iniciando photobooth:\n{str(e)}")

    def abrir_editor_plantillas(self):
        """Abre la lista de plantillas para el evento seleccionado"""
        selected_rows = self.tabla.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Por favor seleccione un evento")
            return

        row = selected_rows[0].row()
        evento_id = int(self.tabla.item(row, 0).text())
        evento_nombre = self.tabla.item(row, 1).text()

        try:
            # Abrir lista de plantillas
            self.templates_window = TemplateListWindow(evento_id, parent=self)
            self.templates_window.show()

            logger.info(f"Lista de plantillas abierta para evento: {evento_nombre}")

        except Exception as e:
            logger.error(f"Error abriendo lista de plantillas: {e}")
            QMessageBox.critical(self, "Error", f"Error abriendo lista de plantillas:\n{str(e)}")
