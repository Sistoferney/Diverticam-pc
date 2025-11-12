"""
Conexión a la base de datos SQLAlchemy
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.pool import StaticPool
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

# Base para los modelos
Base = declarative_base()

# Engine global
engine = None
SessionLocal = None


def init_db():
    """Inicializa la base de datos y crea las tablas"""
    global engine, SessionLocal

    # Crear engine
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Necesario para SQLite
        poolclass=StaticPool,
        echo=False  # Cambiar a True para debug SQL
    )

    # Habilitar foreign keys en SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Crear SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Importar todos los modelos antes de crear tablas
    from . import models

    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)

    # Ejecutar migraciones automáticas
    try:
        from .migrate_add_balance_blancos import migrate_add_balance_blancos
        migrate_add_balance_blancos()
    except Exception as e:
        logger.warning(f"Error ejecutando migraciones: {e}")

    logger.info(f"Base de datos inicializada: {DATABASE_URL}")

    return engine


def get_session() -> Session:
    """
    Obtiene una nueva sesión de base de datos

    Usage:
        with get_session() as session:
            clientes = session.query(Cliente).all()
    """
    if SessionLocal is None:
        init_db()

    return SessionLocal()


def get_engine():
    """Retorna el engine de SQLAlchemy"""
    global engine
    if engine is None:
        init_db()
    return engine
