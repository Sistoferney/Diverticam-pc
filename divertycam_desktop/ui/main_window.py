"""
Ventana principal de DivertyCam Desktop
"""
import logging
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon

import config
from .clientes.clientes_widget import ClientesWidget
from .eventos.eventos_widget import EventosWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(QSize(1200, 700))

        # Crear interfaz
        self.init_ui()

        # Crear menús
        self.init_menus()

        # Crear barra de estado
        self.statusBar().showMessage("Listo")

        logger.info("Ventana principal creada")

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Widget central con tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)

        # Tab de Clientes
        self.clientes_widget = ClientesWidget()
        self.tabs.addTab(self.clientes_widget, "Clientes")

        # Tab de Eventos
        self.eventos_widget = EventosWidget()
        self.tabs.addTab(self.eventos_widget, "Eventos")

        # Tab de Configuración (placeholder por ahora)
        config_widget = QWidget()
        config_layout = QVBoxLayout()
        config_widget.setLayout(config_layout)
        self.tabs.addTab(config_widget, "Configuración")

        # Establecer widget central
        self.setCentralWidget(self.tabs)

    def init_menus(self):
        """Inicializa los menús"""
        menubar = self.menuBar()

        # Menú Archivo
        archivo_menu = menubar.addMenu("&Archivo")

        # Acción: Nuevo Cliente
        nuevo_cliente_action = QAction("Nuevo &Cliente", self)
        nuevo_cliente_action.setShortcut("Ctrl+N")
        nuevo_cliente_action.triggered.connect(self.nuevo_cliente)
        archivo_menu.addAction(nuevo_cliente_action)

        # Acción: Nuevo Evento
        nuevo_evento_action = QAction("Nuevo &Evento", self)
        nuevo_evento_action.setShortcut("Ctrl+E")
        nuevo_evento_action.triggered.connect(self.nuevo_evento)
        archivo_menu.addAction(nuevo_evento_action)

        archivo_menu.addSeparator()

        # Acción: Salir
        salir_action = QAction("&Salir", self)
        salir_action.setShortcut("Ctrl+Q")
        salir_action.triggered.connect(self.close)
        archivo_menu.addAction(salir_action)

        # Menú Photobooth
        photobooth_menu = menubar.addMenu("&Photobooth")

        # Acción: Iniciar Photobooth
        iniciar_photobooth_action = QAction("&Iniciar Photobooth", self)
        iniciar_photobooth_action.setShortcut("F5")
        iniciar_photobooth_action.triggered.connect(self.iniciar_photobooth)
        photobooth_menu.addAction(iniciar_photobooth_action)

        # Menú Ayuda
        ayuda_menu = menubar.addMenu("&Ayuda")

        # Acción: Acerca de
        acerca_action = QAction("&Acerca de", self)
        acerca_action.triggered.connect(self.mostrar_acerca_de)
        ayuda_menu.addAction(acerca_action)

    def nuevo_cliente(self):
        """Abre el diálogo para crear un nuevo cliente"""
        self.tabs.setCurrentIndex(0)  # Cambiar a tab de clientes
        self.clientes_widget.nuevo_cliente()

    def nuevo_evento(self):
        """Abre el diálogo para crear un nuevo evento"""
        self.tabs.setCurrentIndex(1)  # Cambiar a tab de eventos
        self.eventos_widget.nuevo_evento()

    def iniciar_photobooth(self):
        """Inicia el photobooth"""
        # TODO: Implementar ventana de photobooth
        QMessageBox.information(
            self,
            "Photobooth",
            "Función de photobooth en desarrollo"
        )

    def mostrar_acerca_de(self):
        """Muestra el diálogo 'Acerca de'"""
        QMessageBox.about(
            self,
            f"Acerca de {config.APP_NAME}",
            f"""
            <h2>{config.APP_NAME}</h2>
            <p>Versión: {config.APP_VERSION}</p>
            <p>Sistema de gestión de eventos y photobooth profesional</p>
            <p>© 2025 {config.COMPANY_NAME}</p>
            """
        )

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana"""
        reply = QMessageBox.question(
            self,
            "Confirmar salida",
            "¿Está seguro que desea salir?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            logger.info("Cerrando aplicación")
            event.accept()
        else:
            event.ignore()
