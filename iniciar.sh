#!/bin/bash

# Configurar UTF-8 y salida limpia
export LANG=C.UTF-8

echo "======================================================="
echo "    Lanzador de la Aplicación de Facturación y Tiempo"
echo "======================================================="
echo ""

# 1. Comprobar si existe el entorno virtual (.venv)
if [ -f ".venv/bin/python" ]; then
    echo "[OK] Entorno virtual (.venv) detectado."
else
    echo "[INFO] Entorno virtual (.venv) no detectado."
    echo "[INFO] Verificando instalación de Python 3 en el sistema..."

    # 2. Comprobar si Python 3 está instalado
    if ! command -v python3 &> /dev/null; then
        echo "[ERROR] Python 3 no está instalado o no se encuentra en el PATH."
        echo ""
        echo "Por favor instale Python 3 usando el gestor de paquetes de su distribución"
        echo "o descárguelo de https://www.python.org/ (versión 3.8 o superior)."
        echo ""
        read -p "Presione Enter para salir..."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version)
    echo "[OK] Python detectado: $PYTHON_VERSION"

    echo ""
    echo "[PASO 1/3] Creando entorno virtual (.venv)..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual (.venv)."
        read -p "Presione Enter para salir..."
        exit 1
    fi
    echo "[OK] Entorno virtual creado exitosamente."

    echo ""
    echo "[PASO 2/3] Instalando y actualizando dependencias desde requirements.txt..."
    .venv/bin/python -m pip install --upgrade pip
    if [ $? -ne 0 ]; then
        echo "[WARNING] No se pudo actualizar pip, se continuará con la instalación."
    fi

    .venv/bin/python -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Hubo un problema al instalar las dependencias."
        echo "Por favor, compruebe su conexión a Internet y vuelva a intentarlo."
        read -p "Presione Enter para salir..."
        exit 1
    fi
    echo "[OK] Dependencias instaladas correctamente."
fi

# 3. Inicializar base de datos y configuraciones
echo ""
echo "[PASO 3/3] Inicializando base de datos y configuraciones..."
.venv/bin/python initialize_project.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Falló la inicialización del proyecto."
    read -p "Presione Enter para salir..."
    exit 1
fi

echo ""
echo "[OK] Iniciando la aplicación..."
.venv/bin/python facturacion_app/src/main.py
if [ $? -ne 0 ]; then
    echo ""
    echo "[WARNING] La aplicación finalizó con código de error."
    read -p "Presione Enter para salir..."
fi
exit 0
