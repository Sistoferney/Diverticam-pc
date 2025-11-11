# DivertyCam Desktop

Aplicación de escritorio para gestión de eventos y photobooth profesional.

## Descripción

DivertyCam Desktop es una plataforma de administración de eventos que permite:
- Gestionar clientes y eventos
- Ejecutar sesiones de photobooth con captura de fotos
- Generar collages personalizados
- Imprimir resultados en tiempo real

## Características

- **Gestión de Clientes**: CRUD completo para administrar información de clientes
- **Gestión de Eventos**: Crear y configurar eventos con detalles personalizados
- **Photobooth Interactivo**:
  - Captura de fotos con cuenta regresiva
  - Vista previa en tiempo real
  - Soporte para múltiples tipos de cámaras (webcam, DSLR)
- **Collages Personalizables**: Generación automática de collages con plantillas
- **Sistema de Impresión**: Impresión directa desde la aplicación
- **Base de Datos Local**: SQLite para portabilidad y facilidad de uso

## Tecnologías

- **PySide6 (Qt6)**: Framework de interfaz gráfica
- **SQLAlchemy**: ORM para base de datos
- **Pillow**: Procesamiento de imágenes
- **OpenCV**: Captura de cámaras
- **SQLite**: Base de datos embebida

## Requisitos

- Python 3.10 o superior
- Windows 10/11 (Linux/macOS con adaptaciones menores)
- Cámara web o cámara DSLR compatible

## Instalación

### Opción 1: Instalación con entorno virtual (Recomendada)

```bash
cd divertycam_desktop
install_py313.bat
```

### Opción 2: Instalación directa con Python global

Si ya tienes Python 3.13 instalado con PySide6:

```bash
cd divertycam_desktop
run_direct.bat
```

### Instalación manual

```bash
cd divertycam_desktop

# Crear entorno virtual
python -m venv venv_desktop

# Activar entorno
venv_desktop\Scripts\activate

# Instalar dependencias
pip install PySide6 SQLAlchemy Pillow opencv-python

# Ejecutar
python main.py
```

## Uso

### Iniciar la aplicación

```bash
cd divertycam_desktop
run.bat
```

O directamente:

```bash
python divertycam_desktop/main.py
```

### Flujo básico

1. **Registrar Cliente**: Pestaña "Clientes" → Agregar nuevo cliente
2. **Crear Evento**: Pestaña "Eventos" → Configurar evento con detalles
3. **Iniciar Photobooth**: Desde evento → Botón "Photobooth" o F5
4. **Capturar Fotos**: Seguir indicaciones en pantalla
5. **Generar Collage**: Automático al completar sesión
6. **Imprimir**: Opción disponible al finalizar

## Estructura del Proyecto

```
divertycam_desktop/
├── main.py                 # Punto de entrada
├── config.py              # Configuración global
├── database/
│   ├── models.py          # Modelos SQLAlchemy
│   └── connection.py      # Gestión de conexiones
├── ui/
│   ├── main_window.py     # Ventana principal
│   ├── clientes/          # Módulo de clientes
│   ├── eventos/           # Módulo de eventos
│   └── photobooth/        # Módulo de photobooth
├── controllers/
│   ├── camera_manager.py  # Gestión de cámaras
│   ├── base_camera.py     # Clase base para cámaras
│   └── webcam_camera.py   # Implementación webcam
└── utils/
    └── ...                # Utilidades
```

## Solución de Problemas

Si encuentras problemas durante la instalación, consulta:

- [TROUBLESHOOTING.md](divertycam_desktop/TROUBLESHOOTING.md): Guía completa de solución de problemas
- [SOLUCION_RAPIDA.md](divertycam_desktop/SOLUCION_RAPIDA.md): Solución rápida para problemas comunes

### Problemas comunes

**Error: "ModuleNotFoundError: No module named 'PySide6'"**
```bash
cd divertycam_desktop
install_v2.bat
```

**Error: "python no se reconoce como comando"**
- Instalar Python y agregar al PATH
- Descargar: https://www.python.org/downloads/

## Licencia

Este proyecto utiliza PySide6 bajo licencia LGPL, permitiendo uso comercial.

## Desarrollo

### Próximas características

- [ ] Soporte completo para cámaras DSLR (Nikon, Canon)
- [ ] Sistema de plantillas de collage personalizable
- [ ] Impresión térmica directa
- [ ] Sistema de licencias
- [ ] Exportación a .exe standalone
- [ ] Modo kiosco (pantalla completa sin controles)

### Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Contacto

Proyecto: [https://github.com/Sistoferney/Diverticam-pc](https://github.com/Sistoferney/Diverticam-pc)

## Historial de Cambios

### v1.0.0 (2025-01-XX)
- Versión inicial
- Gestión de clientes y eventos
- Photobooth con webcam
- Captura de fotos y sesiones

---

**Nota**: Este proyecto es una migración completa desde Django a una aplicación de escritorio. Para más información sobre la arquitectura y decisiones de diseño, consulta [PROJECTS_GUIDE.md](PROJECTS_GUIDE.md).
