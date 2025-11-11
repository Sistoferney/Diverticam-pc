# DivertyCam Desktop

Sistema de gestión de eventos y photobooth profesional desarrollado con PySide6 y SQLAlchemy.

## Características

- **Gestión de Clientes**: CRUD completo con búsqueda y filtrado
- **Gestión de Eventos**: Vinculación con clientes y múltiples servicios
- **Photobooth**: Sistema de captura con soporte para múltiples cámaras
- **Collages personalizables**: Editor drag-and-drop
- **Impresión automática**: Integración con impresoras Windows
- **Base de datos SQLite**: Portable y sin configuración

## Requisitos

- Python 3.10 o superior
- Windows 10/11 (para funciones de cámara y impresión)

## Instalación

### 1. Crear entorno virtual

```bash
cd divertycam_desktop
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements_desktop.txt
```

## Ejecutar la aplicación

```bash
python main.py
```

## Estructura del proyecto

```
divertycam_desktop/
├── main.py                  # Punto de entrada
├── config.py               # Configuración global
├── requirements_desktop.txt
│
├── database/               # Capa de base de datos
│   ├── connection.py       # SQLAlchemy engine
│   └── models.py           # Modelos (Cliente, Evento, etc.)
│
├── ui/                     # Interfaz de usuario
│   ├── main_window.py      # Ventana principal
│   ├── clientes/           # Módulo de clientes
│   │   ├── clientes_widget.py
│   │   └── cliente_dialog.py
│   ├── eventos/            # Módulo de eventos
│   │   ├── eventos_widget.py
│   │   └── evento_dialog.py
│   └── photobooth/         # Módulo de photobooth (TODO)
│
├── controllers/            # Lógica de negocio
│   └── camera_controller.py
│
└── utils/                  # Utilidades
    └── license_manager.py
```

## Uso básico

### Gestión de Clientes

1. Abrir la pestaña "Clientes"
2. Click en "Nuevo Cliente" o presionar `Ctrl+N`
3. Llenar el formulario con los datos del cliente
4. Guardar

**Funciones disponibles:**
- Búsqueda en tiempo real
- Editar (doble click o botón)
- Eliminar (con confirmación)
- Activar/Desactivar clientes

### Gestión de Eventos

1. Abrir la pestaña "Eventos"
2. Click en "Nuevo Evento" o presionar `Ctrl+E`
3. Seleccionar cliente existente
4. Configurar fecha, dirección y servicios
5. Guardar

**Funciones disponibles:**
- Búsqueda por nombre, cliente o dirección
- Editar eventos
- Eliminar eventos
- Iniciar photobooth para el evento

## Migración desde Django

Si vienes del proyecto Django original:

### Diferencias principales:

| Aspecto | Django (Anterior) | PySide6 (Actual) |
|---------|-------------------|------------------|
| Base de datos | PostgreSQL | SQLite |
| Interfaz | HTML/Templates | Widgets nativos Qt |
| Autenticación | Django Auth | Local (config file) |
| Servidor | Runserver | Aplicación de escritorio |

### Ventajas del nuevo sistema:

✅ **No requiere servidor web**
✅ **Instalación más simple** (un solo ejecutable)
✅ **Mejor rendimiento** para operaciones locales
✅ **Interfaz nativa** de Windows
✅ **Base de datos portable** (archivo único)

## Próximos pasos (Roadmap)

### Fase 1: Completado ✅
- [x] Estructura base del proyecto
- [x] Modelos SQLAlchemy
- [x] CRUD de Clientes
- [x] CRUD de Eventos

### Fase 2: En desarrollo 🚧
- [ ] Ventana de Photobooth
- [ ] Integración con cámaras (PTP/USB/Webcam)
- [ ] Sistema de captura y cuenta regresiva

### Fase 3: Planeado 📋
- [ ] Editor de templates de collage
- [ ] Generación de collages
- [ ] Sistema de impresión
- [ ] Transferencia por WhatsApp

### Fase 4: Futuro 🔮
- [ ] Sistema de licencias
- [ ] Actualizaciones automáticas
- [ ] Modo offline completo

## Desarrollo

### Agregar un nuevo módulo

1. Crear carpeta en `ui/nuevo_modulo/`
2. Crear `__init__.py`
3. Crear widget principal `nuevo_modulo_widget.py`
4. Agregar al `main_window.py` como nueva tab

### Agregar un nuevo modelo

1. Definir clase en `database/models.py` heredando de `Base`
2. Ejecutar para crear la tabla:
```python
from database import init_db
init_db()
```

## Solución de problemas

### Error: "No module named 'PySide6'"

```bash
pip install PySide6
```

### Error de base de datos

Eliminar el archivo de base de datos y reiniciar:
```bash
rm data/divertycam.db
python main.py
```

### Error de importación

Verificar que estás en el directorio correcto:
```bash
cd divertycam_desktop
python main.py
```

## Licencia

Uso comercial permitido. PySide6 está bajo licencia LGPL v3.

---

**DivertyCam Desktop** - Sistema profesional de gestión de eventos
