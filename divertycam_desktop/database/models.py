"""
Modelos de base de datos SQLAlchemy
Migrados desde Django models
"""
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, ForeignKey,
    Text, Date, Float, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class Cliente(Base):
    """Modelo de Cliente"""
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    cedula = Column(String(20), unique=True, nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion = Column(String(255), nullable=False)
    telefono = Column(String(17), nullable=False)

    # Metadatos
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())

    # Relaciones
    eventos = relationship("Evento", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Cliente {self.nombre} {self.apellido} - {self.cedula}>"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Evento(Base):
    """Modelo de Evento"""
    __tablename__ = 'eventos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(100), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    direccion = Column(String(255), nullable=False)

    # Servicios (almacenado como JSON array)
    servicios = Column(JSON, nullable=False, default=list)

    # Foreign Keys
    cliente_id = Column(Integer, ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False)

    # Metadatos
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())

    # Relaciones
    cliente = relationship("Cliente", back_populates="eventos")
    photobooth_config = relationship(
        "PhotoboothConfig",
        back_populates="evento",
        uselist=False,
        cascade="all, delete-orphan"
    )
    collage_templates = relationship(
        "CollageTemplate",
        back_populates="evento",
        cascade="all, delete-orphan"
    )
    collage_sessions = relationship(
        "CollageSession",
        back_populates="evento",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Evento {self.nombre} - {self.fecha_hora}>"


class PhotoboothConfig(Base):
    """Configuración del Photobooth para un evento"""
    __tablename__ = 'photobooth_config'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    evento_id = Column(Integer, ForeignKey('eventos.id', ondelete='CASCADE'), nullable=False, unique=True)

    # Configuración visual
    mensaje_bienvenida = Column(String(200), default='¡Bienvenidos al photobooth!')
    imagen_fondo = Column(String(255), nullable=True)  # Ruta al archivo
    color_texto = Column(String(20), default='#000000')
    tamano_texto = Column(Integer, default=24)
    tipo_letra = Column(String(50), default='Arial')

    # Configuración de captura
    tiempo_entre_fotos = Column(Integer, default=3)
    tiempo_cuenta_regresiva = Column(Integer, default=3)
    tiempo_visualizacion_foto = Column(Integer, default=2)

    # Configuración de cámara
    camera_id = Column(String(255), nullable=True)
    tipo_camara = Column(String(20), default='webcam')  # webcam, nikon_dslr, usb_ptp, windows_camera
    resolucion_camara = Column(String(20), default='1280x720')

    # Configuración DSLR/PTP
    nikon_camera_model = Column(String(100), nullable=True)
    velocidad_obturacion = Column(String(20), default='1/125')
    apertura = Column(String(10), default='f/5.6')
    iso_valor = Column(Integer, default=100)
    modo_disparo = Column(String(20), default='M')
    calidad_imagen = Column(String(20), default='JPEG_FINE')
    modo_enfoque = Column(String(20), default='AF-S')

    # USB/PTP IDs
    usb_vendor_id = Column(String(10), nullable=True)
    usb_product_id = Column(String(10), nullable=True)
    usb_serial_number = Column(String(100), nullable=True)
    usb_connection_status = Column(String(20), default='disconnected')

    # Configuración de impresión
    printer_name = Column(String(255), nullable=True)
    paper_size = Column(String(50), default='10x15')
    copias_impresion = Column(Integer, default=1)
    calidad_impresion = Column(String(20), default='high')
    imprimir_automaticamente = Column(Boolean, default=False)

    # Template de collage
    plantilla_collage_id = Column(String(36), ForeignKey('collage_templates.template_id'), nullable=True)

    # Estado y estadísticas
    activo = Column(Boolean, default=True)
    total_sesiones = Column(Integer, default=0)
    total_fotos = Column(Integer, default=0)
    total_impresiones = Column(Integer, default=0)

    # Metadatos
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, onupdate=func.now())

    # Relaciones
    evento = relationship("Evento", back_populates="photobooth_config")
    plantilla_collage = relationship("CollageTemplate", foreign_keys=[plantilla_collage_id])

    def __repr__(self):
        return f"<PhotoboothConfig para Evento {self.evento_id}>"

    def incrementar_sesiones(self, session):
        self.total_sesiones += 1
        session.commit()

    def incrementar_fotos(self, session, cantidad=1):
        self.total_fotos += cantidad
        session.commit()

    def incrementar_impresiones(self, session, cantidad=1):
        self.total_impresiones += cantidad
        session.commit()


class CollageTemplate(Base):
    """Plantilla de collage personalizada"""
    __tablename__ = 'collage_templates'

    template_id = Column(String(36), primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)

    # Configuración visual
    background_color = Column(String(20), default='#FFFFFF')
    background_image = Column(String(255), nullable=True)
    background_size = Column(String(20), default='cover')
    background_position = Column(String(20), default='center')

    # Datos de la plantilla (JSON con frames, etc.)
    template_data = Column(JSON, nullable=False)

    # Foreign Key
    evento_id = Column(Integer, ForeignKey('eventos.id', ondelete='CASCADE'), nullable=False)

    # Metadatos
    es_predeterminada = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relaciones
    evento = relationship("Evento", back_populates="collage_templates")
    sessions = relationship("CollageSession", back_populates="template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CollageTemplate {self.nombre}>"


class CollageSession(Base):
    """Sesión de fotos para crear un collage"""
    __tablename__ = 'collage_sessions'

    session_id = Column(String(36), primary_key=True)
    status = Column(String(20), default='active')  # active, completed, canceled

    # Foreign Keys
    template_id = Column(String(36), ForeignKey('collage_templates.template_id', ondelete='CASCADE'), nullable=False)
    evento_id = Column(Integer, ForeignKey('eventos.id', ondelete='CASCADE'), nullable=False)

    # Metadatos
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relaciones
    template = relationship("CollageTemplate", back_populates="sessions")
    evento = relationship("Evento", back_populates="collage_sessions")
    photos = relationship("SessionPhoto", back_populates="session", cascade="all, delete-orphan")
    result = relationship("CollageResult", back_populates="session", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CollageSession {self.session_id} - {self.status}>"


class SessionPhoto(Base):
    """Foto individual de una sesión de collage"""
    __tablename__ = 'session_photos'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key
    session_id = Column(String(36), ForeignKey('collage_sessions.session_id', ondelete='CASCADE'), nullable=False)

    frame_index = Column(Integer, nullable=False)
    image_path = Column(String(500), nullable=False)  # Ruta al archivo de imagen
    taken_at = Column(DateTime, server_default=func.now())

    # Relaciones
    session = relationship("CollageSession", back_populates="photos")

    def __repr__(self):
        return f"<SessionPhoto frame {self.frame_index} de session {self.session_id}>"


class CollageResult(Base):
    """Resultado final de un collage"""
    __tablename__ = 'collage_results'

    collage_id = Column(String(36), primary_key=True)

    # Foreign Key
    session_id = Column(String(36), ForeignKey('collage_sessions.session_id', ondelete='CASCADE'), nullable=False, unique=True)

    image_path = Column(String(500), nullable=False)  # Ruta al collage final
    print_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    session = relationship("CollageSession", back_populates="result")

    def __repr__(self):
        return f"<CollageResult {self.collage_id}>"
