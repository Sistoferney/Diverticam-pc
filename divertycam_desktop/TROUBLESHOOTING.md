# Solución de Problemas - DivertyCam Desktop

## ❌ Error: "ModuleNotFoundError: No module named 'PySide6'"

Este error significa que PySide6 no se instaló correctamente.

### Solución 1: Usar el instalador mejorado (Recomendado)

```bash
cd divertycam_desktop
install_v2.bat
```

Este instalador:
- Instala cada dependencia por separado
- Muestra claramente si algo falla
- Verifica la instalación

### Solución 2: Instalación manual paso a paso

```bash
cd divertycam_desktop

# 1. Crear entorno
python -m venv venv_desktop

# 2. Activar
venv_desktop\Scripts\activate

# 3. Actualizar pip
python -m pip install --upgrade pip

# 4. Instalar SOLO PySide6 primero
pip install PySide6

# 5. Verificar
python -c "import PySide6; print('OK')"

# 6. Si funciona, instalar el resto
pip install SQLAlchemy Pillow opencv-python
```

### Solución 3: Ejecutar como Administrador

1. Click derecho en `install_v2.bat`
2. Seleccionar "Ejecutar como administrador"
3. Aceptar el UAC

### Solución 4: Verificar Python

```bash
python --version
```

Debe ser **Python 3.10 o superior**

Si no tienes Python o es una versión antigua:
- Descargar de: https://www.python.org/downloads/
- Durante instalación, marcar "Add Python to PATH"

---

## 🔍 Diagnosticar el problema

Ejecuta el script de diagnóstico:

```bash
cd divertycam_desktop
diagnostico.bat
```

Esto te mostrará:
- ✓ Qué está instalado
- ✗ Qué falta
- Versiones de Python/pip
- Ubicación del entorno virtual

---

## 🐛 Problemas comunes

### Error: "python no se reconoce como comando"

**Causa:** Python no está en el PATH

**Solución:**
1. Reinstalar Python marcando "Add Python to PATH"
2. O agregar manualmente:
   - Panel de Control → Sistema → Variables de entorno
   - Agregar `C:\Users\TU_USUARIO\AppData\Local\Programs\Python\Python3XX` al PATH

### Error: "No se puede conectar a pypi.org"

**Causa:** Problemas de red o firewall

**Soluciones:**
1. Verificar conexión a internet
2. Desactivar VPN temporalmente
3. Desactivar antivirus/firewall temporalmente
4. Usar proxy si estás en red corporativa:
   ```bash
   pip install --proxy http://usuario:pass@proxy:puerto PySide6
   ```

### Error: "Access denied" o "Permission denied"

**Causa:** Sin permisos de escritura

**Soluciones:**
1. Ejecutar como administrador
2. Instalar en otra ubicación (tu carpeta de usuario)
3. Desactivar antivirus temporalmente

### Error: "Microsoft Visual C++ required"

**Causa:** Falta Visual C++ Redistributable (para opencv-python)

**Solución:**
1. Descargar de: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Instalar
3. Reintentar instalación

---

## 🔧 Instalación alternativa (sin script)

Si los scripts no funcionan, hazlo manualmente:

```bash
# 1. Asegúrate de estar en la carpeta correcta
cd e:\copia dc 31-08\DivertyCam-pc\divertycam_desktop

# 2. Crear entorno virtual
python -m venv venv_desktop

# 3. Activar entorno
venv_desktop\Scripts\activate

# Deberías ver (venv_desktop) al inicio de la línea

# 4. Actualizar pip
python -m pip install --upgrade pip

# 5. Instalar cada paquete individualmente
pip install PySide6
pip install SQLAlchemy
pip install Pillow
pip install opencv-python

# 6. Verificar todo
python -c "import PySide6, sqlalchemy, PIL, cv2; print('Todo OK!')"

# 7. Ejecutar aplicación
python main.py
```

---

## 📋 Checklist de requisitos

Antes de instalar, verifica:

- [ ] Python 3.10+ instalado
- [ ] Python en el PATH
- [ ] Permisos de administrador (si es necesario)
- [ ] Conexión a internet funcionando
- [ ] Antivirus no bloqueando pip
- [ ] Al menos 500MB de espacio libre
- [ ] Visual C++ Redistributable (para Windows)

---

## 💡 Consejos

1. **Siempre activa el entorno virtual primero**
   ```bash
   venv_desktop\Scripts\activate
   ```

2. **Verifica que estás usando el Python correcto**
   ```bash
   where python
   # Debe mostrar la ruta dentro de venv_desktop
   ```

3. **Limpia cache de pip si hay problemas**
   ```bash
   pip cache purge
   ```

4. **Reinstala desde cero si nada funciona**
   ```bash
   rmdir /s /q venv_desktop
   install_v2.bat
   ```

---

## 📞 ¿Aún no funciona?

1. Ejecuta `diagnostico.bat` y comparte la salida
2. Revisa los mensajes de error específicos
3. Busca el error en Google con "pip install PySide6 [tu error]"
4. Reporta el issue en GitHub con toda la información

---

## ✅ Instalación exitosa

Si ves esto al final del `install_v2.bat`, todo está bien:

```
✓ PySide6 instalado
✓ SQLAlchemy instalado
✓ Pillow instalado
✓ OpenCV instalado

========================================
INSTALACION COMPLETADA EXITOSAMENTE!
========================================
```

Puedes ejecutar:
```bash
run.bat
```
