"""
Widget de gestión de clientes
"""
import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt

from database import get_session, Cliente
from .cliente_dialog import ClienteDialog

logger = logging.getLogger(__name__)


class ClientesWidget(QWidget):
    """Widget principal para gestión de clientes"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cargar_clientes()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()

        # Barra de herramientas superior
        toolbar = QHBoxLayout()

        # Botón Nuevo
        self.btn_nuevo = QPushButton("Nuevo Cliente")
        self.btn_nuevo.clicked.connect(self.nuevo_cliente)
        toolbar.addWidget(self.btn_nuevo)

        # Botón Editar
        self.btn_editar = QPushButton("Editar")
        self.btn_editar.clicked.connect(self.editar_cliente)
        self.btn_editar.setEnabled(False)
        toolbar.addWidget(self.btn_editar)

        # Botón Eliminar
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_eliminar.setEnabled(False)
        toolbar.addWidget(self.btn_eliminar)

        toolbar.addStretch()

        # Barra de búsqueda
        search_label = QLabel("Buscar:")
        toolbar.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Nombre, cédula, teléfono...")
        self.search_input.textChanged.connect(self.filtrar_clientes)
        toolbar.addWidget(self.search_input)

        # Botón Refrescar
        self.btn_refrescar = QPushButton("Refrescar")
        self.btn_refrescar.clicked.connect(self.cargar_clientes)
        toolbar.addWidget(self.btn_refrescar)

        layout.addLayout(toolbar)

        # Tabla de clientes
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Cédula", "Teléfono", "Activo"
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
        self.tabla.itemDoubleClicked.connect(self.editar_cliente)

        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def cargar_clientes(self):
        """Carga todos los clientes de la base de datos"""
        try:
            with get_session() as session:
                clientes = session.query(Cliente).order_by(Cliente.apellido).all()

                self.tabla.setRowCount(0)  # Limpiar tabla

                for cliente in clientes:
                    self.agregar_cliente_a_tabla(cliente)

            logger.info(f"Cargados {len(clientes)} clientes")

        except Exception as e:
            logger.error(f"Error al cargar clientes: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {str(e)}")

    def agregar_cliente_a_tabla(self, cliente: Cliente):
        """Agrega un cliente a la tabla"""
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)

        self.tabla.setItem(row, 0, QTableWidgetItem(str(cliente.id)))
        self.tabla.setItem(row, 1, QTableWidgetItem(cliente.nombre))
        self.tabla.setItem(row, 2, QTableWidgetItem(cliente.apellido))
        self.tabla.setItem(row, 3, QTableWidgetItem(cliente.cedula))
        self.tabla.setItem(row, 4, QTableWidgetItem(cliente.telefono))
        self.tabla.setItem(row, 5, QTableWidgetItem("Sí" if cliente.activo else "No"))

    def filtrar_clientes(self, texto):
        """Filtra los clientes en la tabla según el texto de búsqueda"""
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

    def nuevo_cliente(self):
        """Abre el diálogo para crear un nuevo cliente"""
        dialog = ClienteDialog(self)

        if dialog.exec():
            self.cargar_clientes()

    def editar_cliente(self):
        """Abre el diálogo para editar el cliente seleccionado"""
        selected_rows = self.tabla.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        cliente_id = int(self.tabla.item(row, 0).text())

        try:
            with get_session() as session:
                cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()

                if cliente:
                    dialog = ClienteDialog(self, cliente)

                    if dialog.exec():
                        self.cargar_clientes()
                else:
                    QMessageBox.warning(self, "Aviso", "Cliente no encontrado")

        except Exception as e:
            logger.error(f"Error al editar cliente: {e}")
            QMessageBox.critical(self, "Error", f"Error al editar cliente: {str(e)}")

    def eliminar_cliente(self):
        """Elimina el cliente seleccionado"""
        selected_rows = self.tabla.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        cliente_id = int(self.tabla.item(row, 0).text())
        nombre = self.tabla.item(row, 1).text()
        apellido = self.tabla.item(row, 2).text()

        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro que desea eliminar al cliente {nombre} {apellido}?\n\n"
            "Esta acción también eliminará todos los eventos asociados.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                with get_session() as session:
                    cliente = session.query(Cliente).filter(Cliente.id == cliente_id).first()

                    if cliente:
                        session.delete(cliente)
                        session.commit()

                        QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
                        self.cargar_clientes()
                    else:
                        QMessageBox.warning(self, "Aviso", "Cliente no encontrado")

            except Exception as e:
                logger.error(f"Error al eliminar cliente: {e}")
                QMessageBox.critical(self, "Error", f"Error al eliminar cliente: {str(e)}")
