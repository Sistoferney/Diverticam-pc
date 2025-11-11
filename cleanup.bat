@echo off
echo ========================================
echo Limpieza del Repositorio DivertyCam
echo ========================================
echo.
echo ADVERTENCIA: Esto eliminara permanentemente:
echo - Proyecto Django completo
echo - node_modules/
echo - Archivos estaticos y media
echo - Scripts de utilidad Django
echo - Archivos de version
echo.
echo Espacio a liberar: ~700MB
echo.
pause
echo.

echo Eliminando proyecto Django...
if exist DivertyCam rmdir /s /q DivertyCam
if exist usuarios rmdir /s /q usuarios
if exist manage.py del /q manage.py
if exist DivertyCam.bat del /q DivertyCam.bat
if exist requirements.txt del /q requirements.txt
if exist venv rmdir /s /q venv
echo   ✓ Proyecto Django eliminado

echo.
echo Eliminando assets y archivos generados...
if exist static rmdir /s /q static
if exist staticfiles rmdir /s /q staticfiles
if exist media rmdir /s /q media
if exist logs rmdir /s /q logs
if exist list_image rmdir /s /q list_image
if exist camara rmdir /s /q camara
echo   ✓ Assets eliminados

echo.
echo Eliminando Node.js...
if exist node_modules rmdir /s /q node_modules
if exist package.json del /q package.json
if exist package-lock.json del /q package-lock.json
echo   ✓ Node.js eliminado

echo.
echo Eliminando scripts de utilidad Django...
if exist find_adb.py del /q find_adb.py
if exist adb_config.txt del /q adb_config.txt
if exist setup_whatsapp_system.py del /q setup_whatsapp_system.py
if exist test_adb_config.py del /q test_adb_config.py
echo   ✓ Scripts eliminados

echo.
echo Eliminando archivos de version...
if exist 1.0.26 del /q 1.0.26
if exist 2.28.0 del /q 2.28.0
if exist 305 del /q 305
if exist 5.8.0 del /q 5.8.0
echo   ✓ Archivos de version eliminados

echo.
echo Eliminando archivos sensibles...
if exist .env del /q .env
echo   ✓ Archivos sensibles eliminados

echo.
echo ========================================
echo LIMPIEZA COMPLETADA
echo ========================================
echo.
echo Ahora el repositorio solo contiene:
echo - divertycam_desktop/ (proyecto principal)
echo - .git/ (historial)
echo - .gitignore
echo - PROJECTS_GUIDE.md
echo - CLEANUP_PLAN.md
echo - cleanup.bat (este script)
echo.
echo Siguiente paso:
echo 1. Revisar que todo este bien
echo 2. git add .
echo 3. git commit -m "Limpieza: eliminar proyecto Django"
echo 4. git push
echo.
pause
