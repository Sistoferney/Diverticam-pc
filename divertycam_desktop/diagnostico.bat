@echo off
echo ========================================
echo DivertyCam Desktop - Diagnostico
echo ========================================
echo.

echo Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    echo Por favor instale Python desde https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Verificando pip...
pip --version
if errorlevel 1 (
    echo ERROR: pip no encontrado
    pause
    exit /b 1
)

echo.
echo Verificando entorno virtual...
if exist venv_desktop (
    echo ✓ Entorno virtual existe: venv_desktop\

    echo.
    echo Activando entorno...
    call venv_desktop\Scripts\activate.bat

    echo.
    echo Python en uso:
    where python

    echo.
    echo Paquetes instalados en el entorno:
    pip list

    echo.
    echo Verificando dependencias requeridas:
    echo.

    python -c "import PySide6; print('✓ PySide6 version:', PySide6.__version__)" 2>nul
    if errorlevel 1 echo ✗ PySide6 NO instalado

    python -c "import sqlalchemy; print('✓ SQLAlchemy version:', sqlalchemy.__version__)" 2>nul
    if errorlevel 1 echo ✗ SQLAlchemy NO instalado

    python -c "import PIL; print('✓ Pillow instalado')" 2>nul
    if errorlevel 1 echo ✗ Pillow NO instalado

    python -c "import cv2; print('✓ OpenCV version:', cv2.__version__)" 2>nul
    if errorlevel 1 echo ✗ OpenCV NO instalado

) else (
    echo ✗ Entorno virtual NO existe
    echo Por favor ejecuta install_v2.bat primero
)

echo.
echo ========================================
echo Diagnostico completado
echo ========================================
pause
