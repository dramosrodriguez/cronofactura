@echo off
:: Configurar codificación UTF-8 para evitar problemas con tildes y caracteres especiales
chcp 65001 >nul
title Gestor de Tiempo y Facturas - Lanzador

echo =======================================================
echo     Lanzador de la Aplicación de Facturación y Tiempo
echo =======================================================
echo.

:: 1. Comprobar si existe el entorno virtual (.venv)
if exist .venv\Scripts\python.exe (
    echo [OK] Entorno virtual (.venv) detectado.
    goto RUN_APP
)

echo [INFO] Entorno virtual (.venv) no detectado.
echo [INFO] Verificando instalación de Python en el sistema...

:: 2. Comprobar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no está instalado o no se encuentra en el PATH del sistema.
    echo.
    echo Por favor:
    echo 1. Descargue e instale Python desde https://www.python.org/ (versión 3.8 o superior)
    echo 2. Asegúrese de marcar la opción "Add Python to PATH" durante la instalación.
    echo 3. Cierre esta ventana y vuelva a ejecutar este archivo.
    echo.
    pause
    exit /b 1
)

:: Mostrar versión detectada
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python detectado: %PYTHON_VERSION%

echo.
echo [PASO 1/3] Creando entorno virtual (.venv)...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual (.venv).
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado exitosamente.

echo.
echo [PASO 2/3] Instalando y actualizando dependencias desde requirements.txt...
.venv\Scripts\python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] No se pudo actualizar pip, se continuará con la instalación de dependencias.
)

.venv\Scripts\python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Hubo un problema al instalar las dependencias de requirements.txt.
    echo Por favor, verifique su conexión a Internet y vuelva a intentarlo.
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas correctamente.

:RUN_APP
echo.
echo [PASO 3/3] Inicializando base de datos y configuraciones...
.venv\Scripts\python initialize_project.py
if %errorlevel% neq 0 (
    echo [ERROR] Falló la inicialización del proyecto.
    pause
    exit /b 1
)

echo.
echo [OK] Iniciando la aplicación...
.venv\Scripts\python facturacion_app\src\main.py
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] La aplicación se cerró con un código de error o advertencia.
    pause
)
exit /b 0
