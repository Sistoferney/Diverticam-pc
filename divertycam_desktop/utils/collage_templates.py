"""
Plantillas predeterminadas para collages
"""
import uuid
from typing import Dict, List, Any


def create_template(
    nombre: str,
    descripcion: str,
    num_photos: int,
    canvas_width: int,
    canvas_height: int,
    frames: List[Dict[str, int]],
    background_color: str = "#FFFFFF",
    spacing: int = 20,
    border_width: int = 5,
    border_color: str = "#FFFFFF"
) -> Dict[str, Any]:
    """
    Crea una plantilla de collage

    Args:
        nombre: Nombre de la plantilla
        descripcion: Descripción
        num_photos: Número de fotos que soporta
        canvas_width: Ancho del canvas en píxeles
        canvas_height: Alto del canvas en píxeles
        frames: Lista de frames, cada uno con x, y, width, height
        background_color: Color de fondo
        spacing: Espaciado entre fotos
        border_width: Ancho del borde alrededor de cada foto
        border_color: Color del borde

    Returns:
        Diccionario con la configuración de la plantilla
    """
    return {
        "template_id": str(uuid.uuid4()),
        "nombre": nombre,
        "descripcion": descripcion,
        "num_photos": num_photos,
        "canvas": {
            "width": canvas_width,
            "height": canvas_height,
            "background_color": background_color
        },
        "frames": frames,
        "styling": {
            "spacing": spacing,
            "border_width": border_width,
            "border_color": border_color
        }
    }


def get_default_templates() -> List[Dict[str, Any]]:
    """
    Retorna lista de plantillas predeterminadas

    Returns:
        Lista de plantillas
    """
    templates = []

    # ==========================================
    # PLANTILLA 2 FOTOS - Vertical
    # ==========================================
    template_2_vertical = create_template(
        nombre="2 Fotos Vertical",
        descripcion="Dos fotos apiladas verticalmente",
        num_photos=2,
        canvas_width=1200,
        canvas_height=1800,
        frames=[
            {"x": 100, "y": 100, "width": 1000, "height": 750},   # Foto superior
            {"x": 100, "y": 950, "width": 1000, "height": 750},   # Foto inferior
        ],
        background_color="#2C3E50",
        spacing=20,
        border_width=10,
        border_color="#FFFFFF"
    )
    templates.append(template_2_vertical)

    # ==========================================
    # PLANTILLA 2 FOTOS - Horizontal
    # ==========================================
    template_2_horizontal = create_template(
        nombre="2 Fotos Horizontal",
        descripcion="Dos fotos lado a lado",
        num_photos=2,
        canvas_width=2400,
        canvas_height=1200,
        frames=[
            {"x": 100, "y": 225, "width": 1000, "height": 750},   # Foto izquierda
            {"x": 1300, "y": 225, "width": 1000, "height": 750},  # Foto derecha
        ],
        background_color="#34495E",
        spacing=20,
        border_width=10,
        border_color="#FFFFFF"
    )
    templates.append(template_2_horizontal)

    # ==========================================
    # PLANTILLA 4 FOTOS - Grid 2x2
    # ==========================================
    template_4_grid = create_template(
        nombre="4 Fotos Grid",
        descripcion="Cuatro fotos en grid 2x2",
        num_photos=4,
        canvas_width=2000,
        canvas_height=2000,
        frames=[
            {"x": 100, "y": 100, "width": 850, "height": 850},     # Superior izquierda
            {"x": 1050, "y": 100, "width": 850, "height": 850},    # Superior derecha
            {"x": 100, "y": 1050, "width": 850, "height": 850},    # Inferior izquierda
            {"x": 1050, "y": 1050, "width": 850, "height": 850},   # Inferior derecha
        ],
        background_color="#1ABC9C",
        spacing=20,
        border_width=8,
        border_color="#FFFFFF"
    )
    templates.append(template_4_grid)

    # ==========================================
    # PLANTILLA 4 FOTOS - Tira Vertical
    # ==========================================
    template_4_strip = create_template(
        nombre="4 Fotos Tira",
        descripcion="Cuatro fotos en tira vertical (estilo fotomatón)",
        num_photos=4,
        canvas_width=800,
        canvas_height=2400,
        frames=[
            {"x": 100, "y": 100, "width": 600, "height": 450},    # Foto 1
            {"x": 100, "y": 650, "width": 600, "height": 450},    # Foto 2
            {"x": 100, "y": 1200, "width": 600, "height": 450},   # Foto 3
            {"x": 100, "y": 1750, "width": 600, "height": 450},   # Foto 4
        ],
        background_color="#E74C3C",
        spacing=15,
        border_width=5,
        border_color="#FFFFFF"
    )
    templates.append(template_4_strip)

    # ==========================================
    # PLANTILLA 6 FOTOS - Grid 3x2
    # ==========================================
    template_6_grid = create_template(
        nombre="6 Fotos Grid",
        descripcion="Seis fotos en grid 3x2",
        num_photos=6,
        canvas_width=2400,
        canvas_height=1800,
        frames=[
            {"x": 100, "y": 100, "width": 650, "height": 650},     # Fila 1, Col 1
            {"x": 850, "y": 100, "width": 650, "height": 650},     # Fila 1, Col 2
            {"x": 1600, "y": 100, "width": 650, "height": 650},    # Fila 1, Col 3
            {"x": 100, "y": 850, "width": 650, "height": 650},     # Fila 2, Col 1
            {"x": 850, "y": 850, "width": 650, "height": 650},     # Fila 2, Col 2
            {"x": 1600, "y": 850, "width": 650, "height": 650},    # Fila 2, Col 3
        ],
        background_color="#9B59B6",
        spacing=15,
        border_width=8,
        border_color="#FFFFFF"
    )
    templates.append(template_6_grid)

    # ==========================================
    # PLANTILLA 6 FOTOS - Tira Doble
    # ==========================================
    template_6_double_strip = create_template(
        nombre="6 Fotos Tira Doble",
        descripcion="Seis fotos en dos columnas verticales",
        num_photos=6,
        canvas_width=1600,
        canvas_height=2400,
        frames=[
            # Columna izquierda
            {"x": 100, "y": 100, "width": 600, "height": 600},
            {"x": 100, "y": 800, "width": 600, "height": 600},
            {"x": 100, "y": 1500, "width": 600, "height": 600},
            # Columna derecha
            {"x": 900, "y": 100, "width": 600, "height": 600},
            {"x": 900, "y": 800, "width": 600, "height": 600},
            {"x": 900, "y": 1500, "width": 600, "height": 600},
        ],
        background_color="#3498DB",
        spacing=15,
        border_width=8,
        border_color="#FFFFFF"
    )
    templates.append(template_6_double_strip)

    return templates


def get_template_by_num_photos(num_photos: int) -> Dict[str, Any]:
    """
    Obtiene la primera plantilla que soporte el número de fotos dado

    Args:
        num_photos: Número de fotos

    Returns:
        Template que soporta ese número de fotos, o None si no existe
    """
    templates = get_default_templates()

    for template in templates:
        if template["num_photos"] == num_photos:
            return template

    return None
