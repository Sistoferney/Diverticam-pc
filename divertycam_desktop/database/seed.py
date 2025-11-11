"""
Funciones para inicializar datos predeterminados en la base de datos
"""
import logging
import json
from .connection import get_session
from .models import CollageTemplate
from utils.collage_templates import get_default_templates

logger = logging.getLogger(__name__)


def seed_default_templates():
    """
    Crea las plantillas predeterminadas en la base de datos si no existen

    Returns:
        int: Número de plantillas creadas
    """
    try:
        with get_session() as session:
            # Verificar si ya existen plantillas
            existing_count = session.query(CollageTemplate).count()

            if existing_count > 0:
                logger.info(f"Ya existen {existing_count} plantillas en la base de datos")
                return 0

            # Obtener plantillas predeterminadas
            default_templates = get_default_templates()

            created_count = 0

            for template_data in default_templates:
                # Crear el registro en la base de datos
                # Nota: Como es una plantilla general (no asociada a un evento específico),
                # necesitamos manejar el evento_id. Por ahora, las plantillas predeterminadas
                # no tienen evento asociado, pero el modelo requiere uno.
                # Solución: Crear una plantilla solo cuando se crea un evento

                # Por ahora, vamos a guardar las plantillas como "globales"
                # modificando el modelo temporalmente o guardándolas de otra forma

                logger.info(f"Plantilla predeterminada disponible: {template_data['nombre']}")
                # No las guardamos aún porque requieren un evento_id

            logger.info(f"Plantillas predeterminadas disponibles: {len(default_templates)}")
            return 0

    except Exception as e:
        logger.error(f"Error inicializando plantillas: {e}", exc_info=True)
        return 0


def create_event_templates(evento_id: int) -> int:
    """
    Crea plantillas predeterminadas para un evento específico

    Args:
        evento_id: ID del evento

    Returns:
        int: Número de plantillas creadas
    """
    try:
        with get_session() as session:
            # Verificar si el evento ya tiene plantillas
            existing_count = session.query(CollageTemplate).filter(
                CollageTemplate.evento_id == evento_id
            ).count()

            if existing_count > 0:
                logger.info(f"El evento {evento_id} ya tiene {existing_count} plantillas")
                return 0

            # Obtener plantillas predeterminadas
            default_templates = get_default_templates()

            created_count = 0

            for template_data in default_templates:
                # Crear plantilla en la base de datos
                template = CollageTemplate(
                    template_id=template_data["template_id"],
                    nombre=template_data["nombre"],
                    descripcion=template_data["descripcion"],
                    background_color=template_data["canvas"]["background_color"],
                    background_image=None,
                    template_data=json.dumps(template_data),  # Guardar como JSON
                    evento_id=evento_id,
                    es_predeterminada=True
                )

                session.add(template)
                created_count += 1

            session.commit()

            logger.info(f"Creadas {created_count} plantillas para el evento {evento_id}")
            return created_count

    except Exception as e:
        logger.error(f"Error creando plantillas para evento: {e}", exc_info=True)
        return 0


def get_or_create_default_template(evento_id: int, num_photos: int = 4) -> str:
    """
    Obtiene o crea una plantilla predeterminada para un evento

    Args:
        evento_id: ID del evento
        num_photos: Número de fotos que debe soportar la plantilla

    Returns:
        str: template_id de la plantilla, o None si hubo error
    """
    try:
        with get_session() as session:
            # Buscar plantilla existente para el evento con el número de fotos
            template = session.query(CollageTemplate).filter(
                CollageTemplate.evento_id == evento_id,
                CollageTemplate.es_predeterminada == True
            ).first()

            if template:
                # Verificar que la plantilla soporte el número de fotos
                template_data = template.template_data
                if isinstance(template_data, str):
                    template_data = json.loads(template_data)

                if template_data.get("num_photos") == num_photos:
                    return template.template_id

            # No existe una plantilla adecuada, crear plantillas para el evento
            created = create_event_templates(evento_id)

            if created > 0:
                # Buscar plantilla con el número de fotos requerido
                all_templates = session.query(CollageTemplate).filter(
                    CollageTemplate.evento_id == evento_id
                ).all()

                for t in all_templates:
                    template_data = t.template_data
                    if isinstance(template_data, str):
                        template_data = json.loads(template_data)

                    if template_data.get("num_photos") == num_photos:
                        return t.template_id

            logger.warning(f"No se encontró plantilla para {num_photos} fotos")
            return None

    except Exception as e:
        logger.error(f"Error obteniendo/creando plantilla: {e}", exc_info=True)
        return None
