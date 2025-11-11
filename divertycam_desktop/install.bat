@echo off
echo ========================================
echo DivertyCam Desktop - Instalador
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

echo [1/4] Creando entorno virtual (venv_desktop)...
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

echo [2/4] Activando entorno virtual...
call venv_desktop\Scripts\activate.bat

echo [3/4] Actualizando pip...
python -m pip install --upgrade pip --quiet

echo [4/5] Instalando dependencias principales...
pip install PySide6 SQLAlchemy Pillow opencv-python

if errorlevel 1 (
    echo.
    echo ADVERTENCIA: Hubo problemas instalando algunas dependencias
    echo Intentando de nuevo con --no-cache-dir...
    pip install --no-cache-dir PySide6 SQLAlchemy Pillow opencv-python
)

echo [5/5] Verificando instalacion...
python -c "import PySide6; import sqlalchemy; print('OK: Dependencias instaladas correctamente')"

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
echo ========================================
echo Para ejecutar la aplicacion:
echo   Opcion 1: Ejecutar run.bat
echo   Opcion 2: Manual
echo     1. Activar entorno: venv_desktop\Scripts\activate
echo     2. Ejecutar: python main.py
echo ========================================
echo.
pause
