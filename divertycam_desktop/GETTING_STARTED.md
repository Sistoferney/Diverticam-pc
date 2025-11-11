# Getting Started - DivertyCam Desktop

Guía rápida para empezar a usar DivertyCam Desktop.

## 🚀 Instalación Rápida

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

### 3. Instalar dependencias

```bash
pip install PySide6 SQLAlchemy Pillow opencv-python
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

## 📝 Primeros pasos

### 1. Crear un cliente

1. Abrir la pestaña "Clientes"
2. Click en "Nuevo Cliente" o presionar `Ctrl+N`
3. Llenar el formulario:
   - Nombre: Juan
   - Apellido: Pérez
   - Cédula: 12345678
   - Fecha de Nacimiento: 01/01/1990
   - Teléfono: +1234567890
   - Dirección: Calle Principal 123
4. Click en "Guardar"

### 2. Crear un evento

1. Abrir la pestaña "Eventos"
2. Click en "Nuevo Evento" o presionar `Ctrl+E`
3. Llenar el formulario:
   - Nombre del Evento: Boda de Juan y María
   - Fecha y Hora: (seleccionar fecha futura)
   - Cliente: Seleccionar el cliente creado
   - Dirección: Salón de eventos XYZ
   - Servicios: Marcar "Cabina fotos"
4. Click en "Guardar"

### 3. Probar el Photobooth

1. En la pestaña "Eventos", seleccionar el evento creado
2. Click en "Iniciar Photobooth"
3. Si es la primera vez, aceptar crear la configuración básica
4. La ventana del photobooth se abrirá mostrando:
   - Preview en vivo de la webcam
   - Mensaje de bienvenida
   - Botones de control

### 4. Capturar fotos

1. En la ventana del photobooth, click en "Iniciar Sesión"
2. Click en "Tomar Foto"
3. Aparecerá una cuenta regresiva (3, 2, 1...)
4. La foto se capturará automáticamente
5. Repetir hasta completar las 4 fotos
6. Al terminar, la sesión se completa automáticamente

## 🎥 Características del Photobooth

### Preview en tiempo real
- La cámara se activa automáticamente al abrir el photobooth
- Preview a ~30 FPS
- Ajuste automático de resolución

### Cuenta regresiva
- Configurable (por defecto 3 segundos)
- Visualización grande en pantalla
- Tiempo entre fotos configurable

### Sesiones
- Cada sesión guarda múltiples fotos
- Fotos almacenadas en `media/photos/`
- Registro en base de datos

### Estados de sesión
- **Activa**: En proceso de captura
- **Completada**: Todas las fotos capturadas
- **Cancelada**: Sesión interrumpida

## 🔧 Configuración

### Cámara

Por defecto usa la webcam del sistema. Para cambiar:

1. En la base de datos, editar `photobooth_config`
2. Cambiar `tipo_camara`:
   - `webcam`: Cámara web USB
   - `nikon_dslr`: Cámara Nikon DSLR (próximamente)
   - `usb_ptp`: Cámara PTP genérica (próximamente)

### Resolución

Editar `config.py`:

```python
CAMERA_SETTINGS = {
    'default_resolution': '1920x1080',  # Cambiar aquí
    ...
}
```

### Tiempos

En `photobooth_config` (base de datos):
- `tiempo_cuenta_regresiva`: Segundos antes de capturar (default: 3)
- `tiempo_entre_fotos`: Segundos entre fotos (default: 3)
- `tiempo_visualizacion_foto`: Segundos mostrando foto (default: 2)

## 📁 Estructura de archivos

```
divertycam_desktop/
├── data/
│   └── divertycam.db          # Base de datos SQLite
├── media/
│   ├── photos/                # Fotos capturadas
│   ├── collages/              # Collages generados
│   ├── backgrounds/           # Fondos de collage
│   └── temp/                  # Archivos temporales
└── logs/
    └── divertycam.log         # Log de la aplicación
```

## 🐛 Solución de problemas

### Error: "No se pudo conectar con la cámara"

**Solución:**
1. Verificar que la webcam esté conectada
2. Cerrar otras aplicaciones que usen la cámara (Zoom, Skype, etc.)
3. Reiniciar la aplicación

### Error: "No module named 'cv2'"

**Solución:**
```bash
pip install opencv-python
```

### La cámara se ve lenta

**Solución:**
1. Cerrar otras aplicaciones
2. Reducir resolución en configuración
3. Verificar que no haya múltiples previews activos

### Base de datos bloqueada

**Solución:**
1. Cerrar todas las instancias de la aplicación
2. Si persiste, eliminar `data/divertycam.db` (se perderán los datos)
3. Reiniciar la aplicación

## 🎯 Próximas características

### En desarrollo:
- ✅ CRUD de Clientes
- ✅ CRUD de Eventos
- ✅ Photobooth básico
- ✅ Captura con webcam
- ⏳ Generación de collages
- ⏳ Sistema de impresión
- ⏳ Cámaras DSLR/PTP

### Planeado:
- Editor de templates de collage
- Transferencia por WhatsApp
- Sistema de licencias
- Compilación a ejecutable (.exe)
- Actualizaciones automáticas

## 💡 Consejos

1. **Iluminación**: Asegúrate de tener buena iluminación para mejores fotos
2. **Posición**: Coloca la cámara a la altura de los ojos
3. **Distancia**: Aproximadamente 1.5-2 metros de la cámara
4. **Fondo**: Usa un fondo limpio o el sistema de fondos virtuales
5. **Pruebas**: Haz varias pruebas antes del evento real

## 📞 Soporte

Para reportar problemas o sugerencias:
- Issues: [GitHub Issues](https://github.com/Sistoferney/Diverticam-pc/issues)
- Email: soporte@divertycam.com

---

**DivertyCam Desktop** - Sistema profesional de gestión de eventos
