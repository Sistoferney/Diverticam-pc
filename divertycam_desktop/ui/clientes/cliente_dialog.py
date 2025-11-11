"""
Diálogo para crear/editar clientes
"""
import logging
from datetime import date
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QDateEdit, QPushButton, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt, QDate

from database import get_session, Cliente

logger = logging.getLogger(__name__)


class ClienteDialog(QDialog):
    """Diálogo para crear o editar un cliente"""

    def __init__(self, parent=None, cliente=None):
        super().__init__(parent)

        self.cliente = cliente
        self.is_edit = cliente is not None

        self.setWindowTitle("Editar Cliente" if self.is_edit else "Nuevo Cliente")
        self.setModal(True)
        self.setMinimumWidth(500)

        self.init_ui()

        if self.is_edit:
            self.cargar_datos()

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        layout = QVBoxLayout()

        # Formulario
        form = QFormLayout()

        # Campo: Nombre
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Ej: Juan")
        form.addRow("Nombre *:", self.nombre_input)

        # Campo: Apellido
        self.apellido_input = QLineEdit()
        self.apellido_input.setPlaceholderText("Ej: Pérez")
        form.addRow("Apellido *:", self.apellido_input)

        # Campo: Cédula
        self.cedula_input = QLineEdit()
        self.cedula_input.setPlaceholderText("Ej: 12345678")
        form.addRow("Cédula *:", self.cedula_input)

        # Campo: Fecha de Nacimiento
        self.fecha_nacimiento_input = QDateEdit()
        self.fecha_nacimiento_input.setCalendarPopup(True)
        self.fecha_nacimiento_input.setDate(QDate.currentDate().addYears(-25))
        self.fecha_nacimiento_input.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Fecha de Nacimiento *:", self.fecha_nacimiento_input)

        # Campo: Teléfono
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Ej: +1234567890")
        form.addRow("Teléfono *:", self.telefono_input)

        # Campo: Dirección
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Ej: Calle 123, Ciudad")
        form.addRow("Dirección *:", self.direccion_input)

        # Campo: Activo
        self.activo_checkbox = QCheckBox()
        self.activo_checkbox.setChecked(True)
        form.addRow("Activo:", self.activo_checkbox)

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

    def cargar_datos(self):
        """Carga los datos del cliente en el formulario"""
        if not self.cliente:
            return

        self.nombre_input.setText(self.cliente.nombre)
        self.apellido_input.setText(self.cliente.apellido)
        self.cedula_input.setText(self.cliente.cedula)

        # Convertir fecha
        if self.cliente.fecha_nacimiento:
            qdate = QDate(
                self.cliente.fecha_nacimiento.year,
                self.cliente.fecha_nacimiento.month,
                self.cliente.fecha_nacimiento.day
            )
            self.fecha_nacimiento_input.setDate(qdate)

        self.telefono_input.setText(self.cliente.telefono)
        self.direccion_input.setText(self.cliente.direccion)
        self.activo_checkbox.setChecked(self.cliente.activo)

    def validar(self):
        """Valida los datos del formulario"""
        errores = []

        # Validar nombre
        if not self.nombre_input.text().strip():
            errores.append("El nombre es obligatorio")
        elif len(self.nombre_input.text().strip()) < 3:
            errores.append("El nombre debe tener al menos 3 caracteres")

        # Validar apellido
        if not self.apellido_input.text().strip():
            errores.append("El apellido es obligatorio")
        elif len(self.apellido_input.text().strip()) < 3:
            errores.append("El apellido debe tener al menos 3 caracteres")

        # Validar cédula
        if not self.cedula_input.text().strip():
            errores.append("La cédula es obligatoria")
        elif len(self.cedula_input.text().strip()) < 5:
            errores.append("La cédula debe tener al menos 5 caracteres")

        # Validar teléfono
        if not self.telefono_input.text().strip():
            errores.append("El teléfono es obligatorio")

        # Validar dirección
        if not self.direccion_input.text().strip():
            errores.append("La dirección es obligatoria")
        elif len(self.direccion_input.text().strip()) < 5:
            errores.append("La dirección debe tener al menos 5 caracteres")

        if errores:
            QMessageBox.warning(
                self,
                "Errores de validación",
                "\n".join([f"• {error}" for error in errores])
            )
            return False

        return True

    def guardar(self):
        """Guarda el cliente en la base de datos"""
        if not self.validar():
            return

        try:
            with get_session() as session:
                if self.is_edit:
                    # Editar cliente existente
                    cliente = session.query(Cliente).filter(Cliente.id == self.cliente.id).first()
                    if not cliente:
                        QMessageBox.warning(self, "Error", "Cliente no encontrado")
                        return
                else:
                    # Crear nuevo cliente
                    cliente = Cliente()

                # Actualizar datos
                cliente.nombre = self.nombre_input.text().strip()
                cliente.apellido = self.apellido_input.text().strip()
                cliente.cedula = self.cedula_input.text().strip()

                # Convertir QDate a date
                qdate = self.fecha_nacimiento_input.date()
                cliente.fecha_nacimiento = date(qdate.year(), qdate.month(), qdate.day())

                cliente.telefono = self.telefono_input.text().strip()
                cliente.direccion = self.direccion_input.text().strip()
                cliente.activo = self.activo_checkbox.isChecked()

                if not self.is_edit:
                    session.add(cliente)

                session.commit()

                QMessageBox.information(
                    self,
                    "Éxito",
                    "Cliente guardado correctamente"
                )

                self.accept()

        except Exception as e:
            logger.error(f"Error al guardar cliente: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al guardar cliente:\n{str(e)}"
            )
