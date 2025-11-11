@echo off
echo ========================================
echo DivertyCam Desktop - Instalador v2
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instale Python 3.10 o superior desde https://www.python.org/
    pause
    exit /b 1
)

echo Verificando version de Python...
python --version

echo.
echo [1/6] Creando entorno virtual (venv_desktop)...
if exist venv_desktop (
    echo El entorno virtual ya existe. Eliminando el anterior...
    rmdir /s /q venv_desktop
)

python -m venv venv_desktop
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [2/6] Activando entorno virtual...
call venv_desktop\Scripts\activate.bat

echo.
echo [3/6] Verificando activacion del entorno...
where python
echo.

echo [4/6] Actualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ADVERTENCIA: No se pudo actualizar pip, pero continuamos...
)

echo.
echo [5/6] Instalando dependencias (esto puede tomar varios minutos)...
echo.

echo Instalando PySide6...
pip install PySide6
if errorlevel 1 (
    echo ERROR: No se pudo instalar PySide6
    echo.
    echo Posibles soluciones:
    echo 1. Verifica tu conexion a internet
    echo 2. Ejecuta como administrador
    echo 3. Desactiva temporalmente el antivirus
    pause
    exit /b 1
)

echo Instalando SQLAlchemy...
pip install SQLAlchemy
if errorlevel 1 (
    echo ERROR: No se pudo instalar SQLAlchemy
    pause
    exit /b 1
)

echo Instalando Pillow...
pip install Pillow
if errorlevel 1 (
    echo ERROR: No se pudo instalar Pillow
    pause
    exit /b 1
)

echo Instalando opencv-python...
pip install opencv-python
if errorlevel 1 (
    echo ERROR: No se pudo instalar opencv-python
    pause
    exit /b 1
)

echo.
echo [6/6] Verificando instalacion...
python -c "import PySide6; print('✓ PySide6 instalado')"
python -c "import sqlalchemy; print('✓ SQLAlchemy instalado')"
python -c "import PIL; print('✓ Pillow instalado')"
python -c "import cv2; print('✓ OpenCV instalado')"

if errorlevel 1 (
    echo.
    echo ERROR: Hubo un problema con la instalacion
    echo Por favor revisa los mensajes de error arriba
    pause
    exit /b 1
)

echo.
echo ========================================
echo INSTALACION COMPLETADA EXITOSAMENTE!
echo ========================================
echo.
echo Todas las dependencias instaladas:
pip list | findstr /i "PySide6 SQLAlchemy Pillow opencv"
echo.
echo ========================================
echo Para ejecutar la aplicacion:
echo   Opcion 1: Ejecutar run.bat
echo   Opcion 2: Manual
echo     1. Activar entorno: venv_desktop\Scripts\activate
echo     2. Ejecutar: python main.py
echo ========================================
echo.
pause
