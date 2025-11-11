@echo off
echo ========================================
echo DivertyCam Desktop - Python 3.13
echo ========================================
echo.

set PYTHON_PATH=C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe

echo Usando Python 3.13 especificamente...
%PYTHON_PATH% --version

echo.
echo [1/5] Creando entorno virtual con Python 3.13...
if exist venv_desktop (
    echo Eliminando entorno anterior...
    rmdir /s /q venv_desktop
)

%PYTHON_PATH% -m venv venv_desktop
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [2/5] Activando entorno virtual...
call venv_desktop\Scripts\activate.bat

echo.
echo [3/5] Verificando Python activo...
python --version
where python
echo.

echo [4/5] Instalando dependencias...
python -m pip install --upgrade pip --quiet

echo Instalando PySide6...
pip install PySide6

echo Instalando SQLAlchemy...
pip install SQLAlchemy

echo Instalando Pillow...
pip install Pillow

echo Instalando opencv-python...
pip install opencv-python

echo.
echo [5/5] Verificando instalacion...
python -c "import PySide6; print('✓ PySide6:', PySide6.__version__)"
python -c "import sqlalchemy; print('✓ SQLAlchemy:', sqlalchemy.__version__)"
python -c "import PIL; print('✓ Pillow: OK')"
python -c "import cv2; print('✓ OpenCV:', cv2.__version__)"

if errorlevel 1 (
    echo.
    echo ERROR: Hubo un problema
    pause
    exit /b 1
)

echo.
echo ========================================
echo INSTALACION COMPLETADA!
echo ========================================
echo.
echo Para ejecutar: run.bat
echo.
pause
