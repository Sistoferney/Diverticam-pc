# Guía de Proyectos - DivertyCam

Este repositorio contiene **DOS proyectos diferentes**:

## 📋 Resumen

| Aspecto | Django (Original) | Desktop (Nuevo) |
|---------|-------------------|-----------------|
| **Carpeta** | Raíz del proyecto | `divertycam_desktop/` |
| **Tipo** | Aplicación Web | Aplicación de Escritorio |
| **Framework** | Django | PySide6 (Qt) |
| **Base de datos** | PostgreSQL | SQLite |
| **Ejecutar** | `DivertyCam.bat` | `divertycam_desktop/run.bat` |
| **Entorno virtual** | `venv/` | `venv_desktop/` |
| **Puerto** | http://localhost:8000 | N/A (ventana nativa) |
| **Uso** | Servidor web con navegador | Aplicación standalone |

## 🌐 Proyecto 1: Django (Original)

### Ubicación
```
DivertyCam-pc/
├── DivertyCam/          ← Configuración Django
├── usuarios/            ← App Django
├── manage.py
├── DivertyCam.bat       ← Script para ejecutar
└── venv/                ← Entorno virtual Django
```

### Para ejecutar:
```bash
# Opción 1: Script automático
DivertyCam.bat

# Opción 2: Manual
venv\Scripts\activate
python manage.py runserver
```

### Características:
- Aplicación web tradicional
- Se abre en el navegador
- Necesita PostgreSQL
- Templates HTML
- Admin de Django

### Cuándo usar:
- Acceso desde múltiples dispositivos
- Acceso remoto vía navegador
- Si ya tienes PostgreSQL configurado

---

## 💻 Proyecto 2: Desktop (Nuevo - PySide6)

### Ubicación
```
DivertyCam-pc/
└── divertycam_desktop/     ← Proyecto nuevo
    ├── main.py             ← Punto de entrada
    ├── install.bat         ← Instalador
    ├── run.bat             ← Ejecutar app
    ├── venv_desktop/       ← Entorno virtual Desktop
    ├── database/           ← Modelos SQLAlchemy
    ├── ui/                 ← Interfaz Qt
    └── controllers/        ← Cámaras
```

### Para instalar:
```bash
cd divertycam_desktop
install.bat
```

### Para ejecutar:
```bash
cd divertycam_desktop
run.bat
```

### Características:
- Aplicación de escritorio nativa
- Ventanas de Windows nativas
- SQLite (sin servidor)
- Interface Qt moderna
- Portable

### Cuándo usar:
- Uso en una sola PC (photobooth)
- No necesitas servidor web
- Mejor rendimiento local
- Fácil distribución (.exe)
- **Ideal para eventos con photobooth**

---

## 🔄 ¿Cuál proyecto usar?

### Usa **Django** si:
- ✅ Ya lo tienes funcionando
- ✅ Necesitas acceso web remoto
- ✅ Múltiples usuarios simultáneos
- ✅ Tienes PostgreSQL configurado

### Usa **Desktop** si:
- ✅ Quieres una app standalone
- ✅ Uso local en eventos
- ✅ No quieres configurar servidor
- ✅ Mejor rendimiento de cámara
- ✅ Planeas vender el software
- ✅ Distribución más fácil

---

## 🚀 Migración Django → Desktop

Si quieres migrar datos del proyecto Django al Desktop:

### 1. Exportar clientes de Django
```bash
# En el proyecto Django
venv\Scripts\activate
python manage.py shell

from usuarios.models import Cliente
import json

clientes = list(Cliente.objects.values())
with open('clientes_export.json', 'w') as f:
    json.dump(clientes, f, indent=2, default=str)
```

### 2. Importar en Desktop
```python
# En divertycam_desktop/
# Crear script import_data.py

import json
from database import get_session, Cliente
from datetime import datetime

with open('../clientes_export.json') as f:
    data = json.load(f)

with get_session() as session:
    for item in data:
        cliente = Cliente(
            nombre=item['nombre'],
            apellido=item['apellido'],
            cedula=item['cedula'],
            # ... resto de campos
        )
        session.add(cliente)
    session.commit()
```

---

## ⚠️ Importante

- **NO ejecutes ambos proyectos al mismo tiempo** si comparten recursos
- Cada proyecto tiene su propia base de datos
- Los cambios en uno NO afectan al otro
- Puedes mantener ambos para diferentes usos

---

## 🎯 Recomendación

**Para photobooth profesional en eventos**: Usa el proyecto **Desktop**

Ventajas:
- ✅ Más rápido (sin overhead de servidor web)
- ✅ Mejor integración con cámaras
- ✅ No depende de conexión/navegador
- ✅ Portable (llevas la PC al evento)
- ✅ Puedes compilar a .exe y vender

**Para gestión web remota**: Usa el proyecto **Django**

Ventajas:
- ✅ Acceso desde cualquier dispositivo
- ✅ Múltiples usuarios simultáneos
- ✅ Admin web incluido
- ✅ Más fácil para reportes/estadísticas

---

## 📞 ¿Preguntas?

**¿Puedo usar ambos?**
Sí, pero mantén bases de datos separadas o implementa sincronización.

**¿Puedo migrar completamente a Desktop?**
Sí, sigue la guía de migración arriba.

**¿Cuál tiene más funciones?**
Desktop tiene las funcionalidades core optimizadas. Django tiene más funciones web.

**¿Cuál proyecto seguirá desarrollándose?**
Desktop es el proyecto principal para commercialización.
