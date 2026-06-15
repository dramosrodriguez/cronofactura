@echo off
REM Configurar codificacion UTF-8 para evitar problemas con tildes y caracteres especiales
chcp 65001 >nul
title Gestor de Tiempo y Facturas - Lanzador

echo =======================================================
echo     Lanzador de la Aplicacion de Facturacion y Tiempo
echo =======================================================
echo.

REM 1. Comprobar si existe el entorno virtual (.venv)
if exist .venv\Scripts\python.exe (
    echo [OK] Entorno virtual .venv detectado.
    goto RUN_APP
)

echo [INFO] Entorno virtual (.venv) no detectado.
echo [INFO] Verificando instalacion de Python en el sistema...

REM 2. Comprobar si Python esta instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH del sistema.
    echo.
    echo Por favor:
    echo 1. Descargue e instale Python desde https://www.python.org/ - version 3.8 o superior
    echo 2. Asegurese de marcar la opcion "Add Python to PATH" durante la instalacion.
    echo 3. Cierre esta ventana y vuelva a ejecutar este archivo.
    echo.
    pause
    exit /b 1
)

REM Mostrar version detectada
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python detectado: %PYTHON_VERSION%

echo.
echo [PASO 1/3] Creando entorno virtual (.venv)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual .venv.
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado exitosamente.

echo.
echo [PASO 2/3] Instalando y actualizando dependencias desde requirements.txt...
.venv\Scripts\python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] No se pudo actualizar pip, se continuara con la instalacion de dependencias.
)

.venv\Scripts\python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema al instalar las dependencias de requirements.txt.
    echo Por favor, verifique su conexion a Internet y vuelva a intentarlo.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas correctamente.

:RUN_APP
echo.
echo [PASO 3/3] Inicializando base de datos y configuraciones...
.venv\Scripts\python initialize_project.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la inicializacion del proyecto.
    pause
    exit /b 1
)

echo.
echo [OK] Iniciando la aplicacion...
start "" .venv\Scripts\pythonw.exe facturacion_app\src\main.py
exit
