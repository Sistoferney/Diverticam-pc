"""
Item gráfico personalizado para marcos de fotos en el editor de collage
"""
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QFont


class ResizeHandle(QGraphicsRectItem):
    """Handle de redimensionamiento en las esquinas del marco"""

    def __init__(self, position: str, parent=None):
        """
        Args:
            position: 'nw', 'ne', 'sw', 'se' (noroeste, noreste, etc.)
            parent: Item padre
        """
        super().__init__(parent)
        self.position = position
        self.handle_size = 10

        # Configurar rectángulo del handle
        self.setRect(0, 0, self.handle_size, self.handle_size)

        # Estilo
        self.setBrush(QBrush(QColor(255, 107, 107)))
        self.setPen(QPen(Qt.NoPen))

        # Hacer arrastrable y seleccionable
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Cursor según posición
        if position == 'nw':
            self.setCursor(Qt.SizeFDiagCursor)
        elif position == 'ne':
            self.setCursor(Qt.SizeBDiagCursor)
        elif position == 'sw':
            self.setCursor(Qt.SizeBDiagCursor)
        elif position == 'se':
            self.setCursor(Qt.SizeFDiagCursor)


class PhotoFrameItem(QGraphicsRectItem):
    """Item gráfico que representa un marco de foto en el canvas"""

    def __init__(self, frame_index: int, width: float, height: float, aspect_ratio: float = 16/9):
        """
        Args:
            frame_index: Índice del marco
            width: Ancho inicial
            height: Alto inicial
            aspect_ratio: Relación de aspecto a mantener
        """
        super().__init__(0, 0, width, height)

        self.frame_index = frame_index
        self.aspect_ratio = aspect_ratio
        self.min_size = 30

        # Estado
        self.is_selected = False
        self.resize_handle_active = None
        self.resize_start_pos = None
        self.resize_start_rect = None

        # Configurar item
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

        # Estilo
        self.normal_pen = QPen(QColor(255, 107, 107), 2, Qt.DashLine)
        self.selected_pen = QPen(QColor(33, 150, 243), 3, Qt.DashLine)
        self.setPen(self.normal_pen)
        self.setBrush(QBrush(QColor(255, 107, 107, 50)))

        # Crear handles de redimensionamiento
        self.handles = {
            'nw': ResizeHandle('nw', self),
            'ne': ResizeHandle('ne', self),
            'sw': ResizeHandle('sw', self),
            'se': ResizeHandle('se', self)
        }

        # Inicialmente ocultos
        for handle in self.handles.values():
            handle.setVisible(False)

        self.update_handles_position()

    def update_handles_position(self):
        """Actualiza la posición de los handles de redimensionamiento"""
        rect = self.rect()
        handle_size = 10
        offset = handle_size / 2

        # Noroeste (esquina superior izquierda)
        self.handles['nw'].setPos(-offset, -offset)

        # Noreste (esquina superior derecha)
        self.handles['ne'].setPos(rect.width() - offset, -offset)

        # Suroeste (esquina inferior izquierda)
        self.handles['sw'].setPos(-offset, rect.height() - offset)

        # Sureste (esquina inferior derecha)
        self.handles['se'].setPos(rect.width() - offset, rect.height() - offset)

    def set_selected(self, selected: bool):
        """Marca el marco como seleccionado o no"""
        self.is_selected = selected

        if selected:
            self.setPen(self.selected_pen)
            self.setBrush(QBrush(QColor(33, 150, 243, 50)))
            # Mostrar handles
            for handle in self.handles.values():
                handle.setVisible(True)
        else:
            self.setPen(self.normal_pen)
            self.setBrush(QBrush(QColor(255, 107, 107, 50)))
            # Ocultar handles
            for handle in self.handles.values():
                handle.setVisible(False)

        self.update()

    def paint(self, painter: QPainter, option, widget=None):
        """Pinta el marco"""
        # Dibujar rectángulo
        super().paint(painter, option, widget)

        # Dibujar etiqueta
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QPen(QColor(255, 107, 107)))

        rect = self.rect()
        label = f"Foto {self.frame_index + 1}"
        painter.drawText(rect, Qt.AlignCenter, label)

    def mousePressEvent(self, event):
        """Maneja el click en el marco"""
        # Verificar si se hizo click en un handle
        for position, handle in self.handles.items():
            if handle.isVisible() and handle.contains(event.pos() - handle.pos()):
                self.resize_handle_active = position
                self.resize_start_pos = event.pos()
                self.resize_start_rect = self.rect()
                event.accept()
                return

        # Si no es un handle, comportamiento normal de arrastre
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Maneja el movimiento del mouse"""
        if self.resize_handle_active:
            # Redimensionamiento
            self.handle_resize(event.pos())
            event.accept()
        else:
            # Arrastre normal
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Maneja la liberación del mouse"""
        self.resize_handle_active = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        super().mouseReleaseEvent(event)

    def handle_resize(self, current_pos: QPointF):
        """Maneja el redimensionamiento del marco manteniendo aspect ratio"""
        if not self.resize_start_pos or not self.resize_start_rect:
            return

        delta = current_pos - self.resize_start_pos
        position = self.resize_handle_active

        # Obtener rectángulo inicial
        rect = QRectF(self.resize_start_rect)

        # Calcular nuevas dimensiones según el handle
        if position == 'se':  # Sureste (esquina inferior derecha)
            new_width = max(self.min_size, rect.width() + delta.x())
            new_height = new_width / self.aspect_ratio

        elif position == 'sw':  # Suroeste (esquina inferior izquierda)
            new_width = max(self.min_size, rect.width() - delta.x())
            new_height = new_width / self.aspect_ratio
            # Ajustar posición X
            new_x = self.resize_start_rect.x() + (self.resize_start_rect.width() - new_width)
            self.setPos(self.pos().x() + delta.x(), self.pos().y())

        elif position == 'ne':  # Noreste (esquina superior derecha)
            new_width = max(self.min_size, rect.width() + delta.x())
            new_height = new_width / self.aspect_ratio
            # Ajustar posición Y
            new_y = self.resize_start_rect.y() + (self.resize_start_rect.height() - new_height)
            self.setPos(self.pos().x(), self.pos().y() + delta.y())

        elif position == 'nw':  # Noroeste (esquina superior izquierda)
            new_width = max(self.min_size, rect.width() - delta.x())
            new_height = new_width / self.aspect_ratio
            # Ajustar posición X e Y
            self.setPos(self.pos().x() + delta.x(), self.pos().y() + delta.y())

        else:
            return

        # Aplicar nuevas dimensiones
        self.setRect(0, 0, new_width, new_height)
        self.update_handles_position()

    def get_frame_data(self) -> dict:
        """Retorna los datos del marco para guardar"""
        pos = self.pos()
        rect = self.rect()

        return {
            'x': int(pos.x()),
            'y': int(pos.y()),
            'width': int(rect.width()),
            'height': int(rect.height())
        }

    def set_frame_data(self, data: dict):
        """Carga datos del marco"""
        self.setPos(data['x'], data['y'])
        self.setRect(0, 0, data['width'], data['height'])
        self.update_handles_position()
