"""
Generador de collages
Combina múltiples fotos en un collage según una plantilla
"""
import logging
from pathlib import Path
from typing import Dict, List, Any, Union, Optional
from PIL import Image, ImageDraw, ImageOps

logger = logging.getLogger(__name__)


class CollageGenerator:
    """Generador de collages a partir de plantillas"""

    def __init__(self, template: Dict[str, Any]):
        """
        Inicializa el generador con una plantilla

        Args:
            template: Diccionario con la configuración de la plantilla
        """
        self.template = template
        self.canvas = None

    def generate(
        self,
        images: List[Union[Image.Image, str, Path]],
        output_path: Union[str, Path],
        add_border: bool = True
    ) -> Optional[Path]:
        """
        Genera un collage a partir de las imágenes

        Args:
            images: Lista de imágenes (PIL Image o rutas)
            output_path: Ruta donde guardar el collage
            add_border: Si agregar bordes a las fotos

        Returns:
            Path al collage generado, o None si hubo error
        """
        try:
            # Validar número de imágenes
            num_photos = self.template["num_photos"]
            if len(images) < num_photos:
                logger.error(f"Se requieren {num_photos} fotos, pero solo se proporcionaron {len(images)}")
                return None

            # Crear canvas
            self._create_canvas()

            # Procesar cada foto
            frames = self.template["frames"]
            for i, (image_input, frame) in enumerate(zip(images, frames)):
                logger.info(f"Procesando foto {i + 1}/{num_photos}")

                # Cargar imagen si es necesario
                if isinstance(image_input, (str, Path)):
                    image = Image.open(image_input)
                else:
                    image = image_input.copy()

                # Procesar y pegar la imagen en el frame
                self._paste_image_in_frame(image, frame, add_border)

            # Guardar resultado
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self.canvas.save(output_path, "JPEG", quality=95)
            logger.info(f"Collage guardado en: {output_path}")

            return output_path

        except Exception as e:
            logger.error(f"Error generando collage: {e}", exc_info=True)
            return None

    def _create_canvas(self):
        """Crea el canvas base para el collage"""
        canvas_config = self.template["canvas"]
        width = canvas_config["width"]
        height = canvas_config["height"]
        bg_color = canvas_config["background_color"]

        # Crear imagen con color de fondo
        self.canvas = Image.new("RGB", (width, height), bg_color)
        logger.info(f"Canvas creado: {width}x{height}, color: {bg_color}")

    def _paste_image_in_frame(
        self,
        image: Image.Image,
        frame: Dict[str, int],
        add_border: bool
    ):
        """
        Procesa y pega una imagen en un frame específico

        Args:
            image: Imagen a pegar
            frame: Diccionario con x, y, width, height
            add_border: Si agregar borde
        """
        # Extraer posición y tamaño del frame
        x = frame["x"]
        y = frame["y"]
        frame_width = frame["width"]
        frame_height = frame["height"]

        # Redimensionar imagen para que encaje en el frame (crop al centro)
        processed_image = self._fit_image_to_frame(image, frame_width, frame_height)

        # Agregar borde si está habilitado
        if add_border:
            styling = self.template.get("styling", {})
            border_width = styling.get("border_width", 0)
            border_color = styling.get("border_color", "#FFFFFF")

            if border_width > 0:
                processed_image = ImageOps.expand(
                    processed_image,
                    border=border_width,
                    fill=border_color
                )

        # Pegar imagen en el canvas
        self.canvas.paste(processed_image, (x, y))

    def _fit_image_to_frame(
        self,
        image: Image.Image,
        target_width: int,
        target_height: int
    ) -> Image.Image:
        """
        Ajusta una imagen al tamaño del frame manteniendo proporción
        y haciendo crop al centro si es necesario

        Args:
            image: Imagen original
            target_width: Ancho objetivo
            target_height: Alto objetivo

        Returns:
            Imagen ajustada
        """
        # Calcular ratio del frame
        target_ratio = target_width / target_height

        # Calcular ratio de la imagen
        img_width, img_height = image.size
        img_ratio = img_width / img_height

        # Determinar cómo redimensionar
        if img_ratio > target_ratio:
            # Imagen es más ancha que el frame, ajustar por altura
            new_height = target_height
            new_width = int(new_height * img_ratio)
        else:
            # Imagen es más alta que el frame, ajustar por ancho
            new_width = target_width
            new_height = int(new_width / img_ratio)

        # Redimensionar imagen
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Crop al centro para que encaje exactamente
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height

        cropped_image = resized_image.crop((left, top, right, bottom))

        return cropped_image

    def add_text_overlay(
        self,
        text: str,
        position: tuple,
        font_size: int = 48,
        color: str = "#FFFFFF"
    ):
        """
        Agrega texto superpuesto al collage

        Args:
            text: Texto a agregar
            position: Tupla (x, y) con la posición
            font_size: Tamaño de la fuente
            color: Color del texto
        """
        if not self.canvas:
            logger.warning("Canvas no creado, no se puede agregar texto")
            return

        try:
            draw = ImageDraw.Draw(self.canvas)

            # Por ahora usar fuente por defecto
            # TODO: Implementar carga de fuentes personalizadas
            draw.text(position, text, fill=color)

            logger.info(f"Texto agregado: '{text}' en posición {position}")

        except Exception as e:
            logger.error(f"Error agregando texto: {e}")

    def add_logo_overlay(
        self,
        logo_path: Union[str, Path],
        position: tuple,
        size: tuple = None,
        opacity: float = 1.0
    ):
        """
        Agrega un logo/marca de agua al collage

        Args:
            logo_path: Ruta al logo
            position: Tupla (x, y) con la posición
            size: Tupla (width, height) opcional para redimensionar
            opacity: Opacidad del logo (0.0 a 1.0)
        """
        if not self.canvas:
            logger.warning("Canvas no creado, no se puede agregar logo")
            return

        try:
            logo = Image.open(logo_path)

            # Redimensionar si se especifica
            if size:
                logo = logo.resize(size, Image.Resampling.LANCZOS)

            # Aplicar opacidad si es necesario
            if opacity < 1.0:
                if logo.mode != 'RGBA':
                    logo = logo.convert('RGBA')

                alpha = logo.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                logo.putalpha(alpha)

            # Pegar logo
            if logo.mode == 'RGBA':
                self.canvas.paste(logo, position, logo)
            else:
                self.canvas.paste(logo, position)

            logger.info(f"Logo agregado en posición {position}")

        except Exception as e:
            logger.error(f"Error agregando logo: {e}")

    def get_canvas(self) -> Optional[Image.Image]:
        """
        Retorna el canvas actual

        Returns:
            Imagen del canvas, o None si no se ha creado
        """
        return self.canvas
