@echo off
echo ========================================
echo Test de Instalacion - Diagnostico
echo ========================================
echo.

echo [TEST 1] Verificando Python...
python --version
if errorlevel 1 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)
echo.

echo [TEST 2] Verificando pip...
pip --version
echo.

echo [TEST 3] Creando entorno de prueba...
if exist test_venv (
    rmdir /s /q test_venv
)
python -m venv test_venv
echo.

echo [TEST 4] Activando entorno...
call test_venv\Scripts\activate.bat
echo.

echo [TEST 5] Verificando que el entorno esta activo...
where python
echo.

echo [TEST 6] Intentando instalar PySide6 (esto puede tardar)...
echo NOTA: Si se queda mucho tiempo aqui, presiona Ctrl+C
pip install PySide6 --verbose
echo.

if errorlevel 1 (
    echo.
    echo ========================================
    echo FALLO LA INSTALACION DE PySide6
    echo ========================================
    echo.
    echo Posibles causas:
    echo 1. Sin conexion a internet
    echo 2. Firewall/Antivirus bloqueando
    echo 3. Proxy necesario
    echo 4. Falta espacio en disco
    echo.
    pause
    exit /b 1
)

echo [TEST 7] Verificando instalacion...
python -c "import PySide6; print('PySide6 instalado OK!')"

if errorlevel 1 (
    echo ERROR: PySide6 no se puede importar
    pause
    exit /b 1
)

echo.
echo ========================================
echo TEST EXITOSO!
echo ========================================
echo PySide6 se instalo correctamente
echo.
echo Ahora puedes ejecutar install_v2.bat
echo.

REM Limpiar
echo Limpiando entorno de prueba...
deactivate
rmdir /s /q test_venv

pause
