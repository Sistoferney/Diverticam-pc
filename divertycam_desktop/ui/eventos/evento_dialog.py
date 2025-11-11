"""
Diálogo para crear/editar eventos
"""
import logging
import json
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDateTimeEdit, QPushButton, QMessageBox,
    QComboBox, QTextEdit, QCheckBox, QListWidget, QLabel
)
from PySide6.QtCore import Qt, QDateTime

from database import get_session, Evento, Cliente

logger = logging.getLogger(__name__)


class EventoDialog(QDialog):
    """Diálogo para crear o editar un evento"""

    # Opciones de servicios
    SERVICIOS_CHOICES = [
        ('photobook', 'Photobook'),
        ('foto_tradicional', 'Foto tradicional'),
        ('video', 'Video'),
        ('cabina_360', 'Cabina 360'),
        ('cabina_fotos', 'Cabina fotos'),
        ('drone', 'Drone'),
        ('clip_inicio', 'Clip de inicio'),
    ]

    def __init__(self, parent=None, evento=None):
        super().__init__(parent)

        self.evento = evento
        self.is_edit = evento is not None

        self.setWindowTitle("Editar Evento" if self.is_edit else "Nuevo Evento")
        self.setModal(True)
        self.setMinimumWidth(600)

        self.init_ui()
        self.cargar_clientes()

        if self.is_edit:
            self.cargar_datos()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()

        # Formulario
        form = QFormLayout()

        # Campo: Nombre del evento
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Boda de Juan y María")
        form.addRow("Nombre del Evento *:", self.nombre_input)

        # Campo: Fecha y hora
        self.fecha_hora_input = QDateTimeEdit()
        self.fecha_hora_input.setCalendarPopup(True)
        self.fecha_hora_input.setDateTime(QDateTime.currentDateTime())
        self.fecha_hora_input.setDisplayFormat("dd/MM/yyyy HH:mm")
        form.addRow("Fecha y Hora *:", self.fecha_hora_input)

        # Campo: Cliente (ComboBox)
        self.cliente_combo = QComboBox()
        form.addRow("Cliente *:", self.cliente_combo)

        # Campo: Dirección
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Ej: Salón de eventos, Calle 123")
        form.addRow("Dirección *:", self.direccion_input)

        # Campo: Servicios (checkboxes)
        servicios_label = QLabel("Servicios *:")
        form.addRow(servicios_label)

        self.servicios_checkboxes = {}
        for key, label in self.SERVICIOS_CHOICES:
            checkbox = QCheckBox(label)
            self.servicios_checkboxes[key] = checkbox
            form.addRow("", checkbox)

        layout.addLayout(form)

        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(self.btn_cancelar)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)
        self.btn_guardar.setDefault(True)
        buttons_layout.addWidget(self.btn_guardar)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def cargar_clientes(self):
        """Carga los clientes en el ComboBox"""
        try:
            with get_session() as session:
                clientes = session.query(Cliente).filter(Cliente.activo == True).order_by(Cliente.apellido).all()

                self.cliente_combo.clear()
                self.cliente_combo.addItem("-- Seleccionar Cliente --", None)

                for cliente in clientes:
                    self.cliente_combo.addItem(
                        f"{cliente.nombre_completo} - {cliente.cedula}",
                        cliente.id
                    )

        except Exception as e:
            logger.error(f"Error al cargar clientes: {e}")
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {str(e)}")

    def cargar_datos(self):
        """Carga los datos del evento en el formulario"""
        if not self.evento:
            return

        self.nombre_input.setText(self.evento.nombre)

        # Convertir fecha/hora
        if self.evento.fecha_hora:
            qdatetime = QDateTime(
                self.evento.fecha_hora.year,
                self.evento.fecha_hora.month,
                self.evento.fecha_hora.day,
                self.evento.fecha_hora.hour,
                self.evento.fecha_hora.minute
            )
            self.fecha_hora_input.setDateTime(qdatetime)

        # Seleccionar cliente
        if self.evento.cliente_id:
            index = self.cliente_combo.findData(self.evento.cliente_id)
            if index >= 0:
                self.cliente_combo.setCurrentIndex(index)

        self.direccion_input.setText(self.evento.direccion)

        # Marcar servicios
        if self.evento.servicios:
            if isinstance(self.evento.servicios, list):
                servicios_list = self.evento.servicios
            else:
                try:
                    servicios_list = json.loads(self.evento.servicios)
                except:
                    servicios_list = []

            for servicio in servicios_list:
                if servicio in self.servicios_checkboxes:
                    self.servicios_checkboxes[servicio].setChecked(True)

    def validar(self):
        """Valida los datos del formulario"""
        errores = []

        # Validar nombre
        if not self.nombre_input.text().strip():
            errores.append("El nombre del evento es obligatorio")
        elif len(self.nombre_input.text().strip()) < 7:
            errores.append("El nombre del evento debe tener al menos 7 caracteres")

        # Validar cliente
        if self.cliente_combo.currentData() is None:
            errores.append("Debe seleccionar un cliente")

        # Validar dirección
        if not self.direccion_input.text().strip():
            errores.append("La dirección es obligatoria")

        # Validar servicios
        servicios_seleccionados = [key for key, checkbox in self.servicios_checkboxes.items() if checkbox.isChecked()]
        if not servicios_seleccionados:
            errores.append("Debe seleccionar al menos un servicio")

        if errores:
            QMessageBox.warning(
                self,
                "Errores de validación",
                "\n".join([f"• {error}" for error in errores])
            )
            return False

        return True

    def guardar(self):
        """Guarda el evento en la base de datos"""
        if not self.validar():
            return

        try:
            with get_session() as session:
                if self.is_edit:
                    # Editar evento existente
                    evento = session.query(Evento).filter(Evento.id == self.evento.id).first()
                    if not evento:
                        QMessageBox.warning(self, "Error", "Evento no encontrado")
                        return
                else:
                    # Crear nuevo evento
                    evento = Evento()

                # Actualizar datos
                evento.nombre = self.nombre_input.text().strip()

                # Convertir QDateTime a datetime
                qdatetime = self.fecha_hora_input.dateTime()
                evento.fecha_hora = datetime(
                    qdatetime.date().year(),
                    qdatetime.date().month(),
                    qdatetime.date().day(),
                    qdatetime.time().hour(),
                    qdatetime.time().minute()
                )

                evento.cliente_id = self.cliente_combo.currentData()
                evento.direccion = self.direccion_input.text().strip()

                # Guardar servicios como lista JSON
                servicios_seleccionados = [
                    key for key, checkbox in self.servicios_checkboxes.items()
                    if checkbox.isChecked()
                ]
                evento.servicios = servicios_seleccionados

                if not self.is_edit:
                    session.add(evento)

                session.commit()

                QMessageBox.information(
                    self,
                    "Éxito",
                    "Evento guardado correctamente"
                )

                self.accept()

        except Exception as e:
            logger.error(f"Error al guardar evento: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar evento:\n{str(e)}"
            )
