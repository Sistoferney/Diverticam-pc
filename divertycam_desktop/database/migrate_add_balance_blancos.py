"""
Migración: Agregar campo balance_blancos a photobooth_config
"""
import logging
from sqlalchemy import text
from .connection import get_engine

logger = logging.getLogger(__name__)


def migrate_add_balance_blancos():
    """Agrega el campo balance_blancos a la tabla photobooth_config si no existe"""
    engine = get_engine()

    try:
        with engine.connect() as conn:
            # Verificar si la columna ya existe
            result = conn.execute(text("PRAGMA table_info(photobooth_config)"))
            columns = [row[1] for row in result]

            if 'balance_blancos' not in columns:
                logger.info("Agregando columna 'balance_blancos' a photobooth_config...")

                # Agregar la columna
                conn.execute(text(
                    "ALTER TABLE photobooth_config ADD COLUMN balance_blancos VARCHAR(20) DEFAULT 'auto'"
                ))
                conn.commit()

                logger.info("Columna 'balance_blancos' agregada exitosamente")
            else:
                logger.info("Columna 'balance_blancos' ya existe")

    except Exception as e:
        logger.error(f"Error en migración: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    migrate_add_balance_blancos()
