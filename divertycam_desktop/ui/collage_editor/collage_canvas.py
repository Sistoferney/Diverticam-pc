"""
Canvas interactivo para editar plantillas de collage
"""
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPen, QBrush, QPainter, QPixmap, QImage
from PIL import Image
from .photo_frame_item import PhotoFrameItem


class CollageCanvas(QGraphicsScene):
    """Escena gráfica para el editor de collage"""

    # Señales
    frame_selected = Signal(PhotoFrameItem)  # Cuando se selecciona un marco
    frame_deselected = Signal()  # Cuando se deselecciona

    def __init__(self, width_cm: float = 15, height_cm: float = 10, aspect_ratio: float = 16/9):
        """
        Args:
            width_cm: Ancho del canvas en centímetros
            height_cm: Alto del canvas en centímetros
            aspect_ratio: Relación de aspecto de la cámara
        """
        # Conversión cm a píxeles (96 DPI)
        self.cm_to_pixel = 37.8
        width_px = width_cm * self.cm_to_pixel
        height_px = height_cm * self.cm_to_pixel

        super().__init__(0, 0, width_px, height_px)

        self.width_cm = width_cm
        self.height_cm = height_cm
        self.aspect_ratio = aspect_ratio

        # Frames
        self.frames = []
        self.selected_frame = None
        self.frame_counter = 0

        # Estilo del canvas
        self.background_color = QColor(255, 255, 255)
        self.background_image = None
        self.overlay_image = None
        self.overlay_opacity = 1.0

        self.setBackgroundBrush(QBrush(self.background_color))

    def add_frame(self, width: float = 100, height: float = None) -> PhotoFrameItem:
        """Agrega un nuevo marco al canvas"""
        # Calcular altura según aspect ratio si no se proporciona
        if height is None:
            height = width / self.aspect_ratio

        # Crear marco
        frame = PhotoFrameItem(self.frame_counter, width, height, self.aspect_ratio)
        self.frame_counter += 1

        # Posición inicial (centrado)
        canvas_rect = self.sceneRect()
        x = (canvas_rect.width() - width) / 2
        y = (canvas_rect.height() - height) / 2
        frame.setPos(x, y)

        # Agregar a la escena
        self.addItem(frame)
        self.frames.append(frame)

        # Seleccionar automáticamente
        self.select_frame(frame)

        return frame

    def select_frame(self, frame: PhotoFrameItem):
        """Selecciona un marco"""
        # Deseleccionar anterior
        if self.selected_frame:
            self.selected_frame.set_selected(False)

        # Seleccionar nuevo
        self.selected_frame = frame
        frame.set_selected(True)

        # Emitir señal
        self.frame_selected.emit(frame)

    def deselect_frame(self):
        """Deselecciona el marco actual"""
        if self.selected_frame:
            self.selected_frame.set_selected(False)
            self.selected_frame = None
            self.frame_deselected.emit()

    def delete_selected_frame(self):
        """Elimina el marco seleccionado"""
        if self.selected_frame:
            self.removeItem(self.selected_frame)
            self.frames.remove(self.selected_frame)
            self.selected_frame = None
            self.frame_deselected.emit()

    def clear_all_frames(self):
        """Elimina todos los marcos"""
        for frame in self.frames[:]:
            self.removeItem(frame)

        self.frames.clear()
        self.selected_frame = None
        self.frame_counter = 0
        self.frame_deselected.emit()

    def set_background_color(self, color: QColor):
        """Cambia el color de fondo"""
        self.background_color = color
        self.setBackgroundBrush(QBrush(color))

    def set_background_image(self, image_path: str):
        """Establece una imagen de fondo"""
        try:
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.background_image = pixmap
                # Crear un brush con la imagen
                brush = QBrush(pixmap.scaled(
                    int(self.width()),
                    int(self.height()),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                ))
                self.setBackgroundBrush(brush)
        except Exception as e:
            print(f"Error cargando imagen de fondo: {e}")

    def remove_background_image(self):
        """Elimina la imagen de fondo"""
        self.background_image = None
        self.setBackgroundBrush(QBrush(self.background_color))

    def get_template_data(self) -> dict:
        """Retorna los datos de la plantilla actual"""
        # Obtener datos de todos los frames
        frames_data = []
        for frame in self.frames:
            frames_data.append(frame.get_frame_data())

        return {
            'num_photos': len(self.frames),
            'canvas': {
                'width': int(self.width()),
                'height': int(self.height()),
                'background_color': self.background_color.name()
            },
            'frames': frames_data,
            'styling': {
                'spacing': 20,
                'border_width': 10,
                'border_color': '#FFFFFF'
            }
        }

    def load_template_data(self, template_data: dict):
        """Carga datos de una plantilla"""
        # Limpiar frames existentes
        self.clear_all_frames()

        # Cargar color de fondo
        if 'canvas' in template_data and 'background_color' in template_data['canvas']:
            color = QColor(template_data['canvas']['background_color'])
            self.set_background_color(color)

        # Cargar frames
        if 'frames' in template_data:
            for frame_data in template_data['frames']:
                # Crear frame con dimensiones correctas
                width = frame_data['width']
                height = frame_data['height']

                frame = PhotoFrameItem(self.frame_counter, width, height, self.aspect_ratio)
                self.frame_counter += 1

                # Establecer posición
                frame.setPos(frame_data['x'], frame_data['y'])

                # Agregar a la escena
                self.addItem(frame)
                self.frames.append(frame)

    def mousePressEvent(self, event):
        """Maneja clicks en el canvas"""
        item = self.itemAt(event.scenePos(), self.views()[0].transform())

        if isinstance(item, PhotoFrameItem):
            self.select_frame(item)
        elif not item:
            # Click en espacio vacío - deseleccionar
            self.deselect_frame()

        super().mousePressEvent(event)


class CollageCanvasView(QGraphicsView):
    """Vista del canvas de collage"""

    def __init__(self, scene: CollageCanvas):
        super().__init__(scene)

        # Configuración de la vista
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Estilo
        self.setStyleSheet("""
            QGraphicsView {
                border: 2px solid #ddd;
                background-color: #f5f5f5;
            }
        """)

        # Zoom inicial para que se vea completo
        self.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """Zoom con la rueda del mouse"""
        # Zoom factor
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        # Guardar la escena antes del zoom
        old_pos = self.mapToScene(event.position().toPoint())

        # Aplicar zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

        # Obtener la nueva posición
        new_pos = self.mapToScene(event.position().toPoint())

        # Mover la escena para mantener el cursor en el mismo punto
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
