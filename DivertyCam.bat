@echo off
SET CURRENT_DIR=%CD%

:: Ir al directorio donde está el entorno virtual
cd /d %CURRENT_DIR%

:: Activar entorno virtual
call "%CURRENT_DIR%\venv\Scripts\activate.bat"

:: Verificar si el entorno virtual está activado
echo %VIRTUAL_ENV%

:: Ejecutar el servidor de Django
start python manage.py runserver

:: Esperar un segundo para que el servidor se inicie (ajustar si es necesario)
timeout /t 2 /nobreak

:: Abrir el navegador en la dirección local
start http://127.0.0.1:8000/

:: Mantener la ventana del terminal abierta
pause
