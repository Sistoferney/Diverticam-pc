@echo off
echo Iniciando DivertyCam Desktop...

if not exist venv_desktop (
    echo ERROR: Entorno virtual no encontrado
    echo Por favor ejecuta install.bat primero
    pause
    exit /b 1
)

call venv_desktop\Scripts\activate.bat
python main.py
pause
