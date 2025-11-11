# Plan de Limpieza del Repositorio

## 🗑️ Archivos y carpetas a ELIMINAR

### Proyecto Django (completo)
```
DivertyCam/                  ← Configuración Django
usuarios/                    ← App Django
manage.py                    ← Django CLI
DivertyCam.bat              ← Script para ejecutar Django
requirements.txt            ← Dependencias Django (conflicto con Desktop)
venv/                       ← Entorno virtual Django (GRANDE)
```

### Assets y archivos generados
```
static/                     ← Archivos estáticos Django
staticfiles/                ← Archivos compilados Django
media/                      ← Media de Django (imágenes subidas)
logs/                       ← Logs de Django
list_image/                 ← Imágenes del proyecto Django
camara/                     ← ¿Carpeta de cámara vieja?
```

### Node.js (para SweetAlert)
```
node_modules/               ← Dependencias npm (GRANDE)
package.json                ← Config npm
package-lock.json           ← Lock npm
```

### Scripts de utilidad Django
```
find_adb.py                 ← Buscar ADB (usado por Django)
adb_config.txt              ← Config ADB
setup_whatsapp_system.py    ← Setup WhatsApp (Django)
test_adb_config.py          ← Tests ADB
```

### Archivos de versión raros
```
1.0.26
2.28.0
305
5.8.0
```

### Archivos sensibles
```
.env                        ← Variables de entorno (puede tener secretos)
```

## ✅ Archivos a MANTENER

```
divertycam_desktop/         ← PROYECTO PRINCIPAL
.git/                       ← Historial de git
.gitignore                  ← Actualizado
.vscode/                    ← Configuración de VS Code (opcional)
PROJECTS_GUIDE.md           ← Documentación (actualizar)
README.md                   ← Crear nuevo README limpio
```

## 📊 Espacio a liberar

Estimado:
- venv/: ~500MB
- node_modules/: ~100MB
- media/staticfiles/: ~50MB+
- Otros archivos Django: ~50MB

**Total aproximado: ~700MB**

## ⚠️ IMPORTANTE

**Antes de eliminar:**
- ✅ Todo está en commits de git (puedes recuperarlo)
- ✅ Tienes backup local (copia de la carpeta si quieres)
- ✅ El proyecto Desktop es completamente independiente

**No se puede deshacer fácilmente**, pero siempre puedes:
```bash
git checkout <commit_anterior> -- <archivo>
```

## 🚀 Siguiente paso

Ejecutar:
```bash
cleanup.bat
```

Esto eliminará todo lo marcado arriba.
