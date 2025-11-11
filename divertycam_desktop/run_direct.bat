@echo off
echo ========================================
echo DivertyCam Desktop - Ejecucion Directa
echo ========================================
echo.
echo NOTA: Esto usa Python 3.13 global (sin entorno virtual)
echo.

set PYTHON_PATH=C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe

echo Verificando Python...
%PYTHON_PATH% --version

echo.
echo Verificando dependencias...
%PYTHON_PATH% -c "import PySide6; print('✓ PySide6:', PySide6.__version__)" || goto :error
%PYTHON_PATH% -c "import sqlalchemy; print('✓ SQLAlchemy')" || goto :install_missing
%PYTHON_PATH% -c "import PIL; print('✓ Pillow')" || goto :install_missing
%PYTHON_PATH% -c "import cv2; print('✓ OpenCV')" || goto :install_missing

echo.
echo Iniciando DivertyCam Desktop...
%PYTHON_PATH% main.py
goto :end

:install_missing
echo.
echo Instalando dependencias faltantes...
%PYTHON_PATH% -m pip install SQLAlchemy Pillow opencv-python
echo.
echo Iniciando DivertyCam Desktop...
%PYTHON_PATH% main.py
goto :end

:error
echo.
echo ERROR: PySide6 no esta instalado en Python 3.13
echo Ejecuta: install_py313.bat
pause
exit /b 1

:end
pause
