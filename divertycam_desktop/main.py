"""
DivertyCam Desktop - Aplicación principal
Sistema de gestión de eventos y photobooth
"""
import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

# Importar configuración
import config

# Importar base de datos
from database import init_db

# Importar ventana principal
from ui.main_window import MainWindow


def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )


def main():
    """Función principal de la aplicación"""
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Iniciando {config.APP_NAME} v{config.APP_VERSION}")

    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName(config.COMPANY_NAME)

    # Inicializar base de datos
    try:
        logger.info("Inicializando base de datos...")
        init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        return 1

    # Crear y mostrar ventana principal
    try:
        logger.info("Creando ventana principal...")
        window = MainWindow()
        window.show()
        logger.info("Aplicación lista")
    except Exception as e:
        logger.error(f"Error al crear ventana principal: {e}")
        return 1

    # Ejecutar aplicación
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
