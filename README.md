# Gestor de Tiempos y Facturas v0.1.0

Una aplicación de escritorio local moderna y ligera diseñada para profesionales autónomos y pequeñas empresas. Permite llevar un registro pormenorizado de las horas dedicadas a cada cliente, gestionar tarifas por hora o presupuestos por proyecto, y generar facturas profesionales en formato PDF de forma automática con un solo clic.

---

## Características Principales

*   **Registro de Tiempos Sencillo**: Registra horas dedicadas con descripciones detalladas y fechas.
*   **Gestión de Clientes**: Base de datos local para añadir, editar o eliminar clientes con tarifas horarias personalizadas.
*   **Facturación Flexible**:
    *   **Por Horas**: Selecciona las tareas específicas trabajadas en un rango de fechas y genera la factura con el desglose exacto de horas.
    *   **Por Proyecto**: Factura un concepto global cerrado con un importe personalizado, asociando opcionalmente tareas de control.
*   **Generación de PDFs Automática**: Plantilla elegante y profesional (HTML/CSS renderizado a PDF local) que se guarda directamente en tu equipo.
*   **Exportación de Datos**: Exporta listados completos de facturas a Excel y de tiempos registrados a formato CSV.
*   **Configuración Atómica de Emisor**: Guarda tus datos fiscales (Nombre, NIF, Cuenta Bancaria, Dirección, etc.) y tasas de impuestos por defecto (IVA e IRPF) de forma segura.
*   **Base de Datos Local Segura**: Utiliza SQLite bajo el modo de alto rendimiento y seguridad WAL (Write-Ahead Logging).

---

## Requisitos Previos

Antes de ejecutar la aplicación, debes tener instalado en tu sistema:
*   **Python 3.8 o superior** (Descárgalo desde [python.org](https://www.python.org/)).
    *   *Importante (Windows)*: Al instalar, asegúrate de marcar la casilla **"Add Python to PATH"** (Agregar Python al PATH).

---

## Guía de Instalación y Arranque Rápido

Para simplificar el uso de la aplicación, se han creado scripts automatizados en la raíz del proyecto. Estos scripts detectan si tienes configurado el entorno virtual, instalan las dependencias necesarias de forma transparente y arrancan la aplicación.

### En Windows (Fácil)
1. Haz doble clic sobre el archivo **`iniciar.bat`** en la raíz del proyecto.
2. Si es la primera vez que se ejecuta:
    *   Comprobará que Python está instalado en tu sistema.
    *   Creará una carpeta `.venv` con el entorno virtual.
    *   Instalará de manera automatizada las dependencias requeridas (`requirements.txt`).
    *   Creará la base de datos y un archivo de configuración inicial con datos genéricos de prueba.
3. Tras la instalación inicial, la aplicación se iniciará de forma automática.
4. En las siguientes ocasiones, al hacer doble clic en `iniciar.bat`, la aplicación arrancará instantáneamente sin reinstalar nada.

### En macOS / Linux
1. Abre un terminal en la carpeta raíz del proyecto.
2. Otorga permisos de ejecución al script lanzador:
   ```bash
   chmod +x iniciar.sh
   ```
3. Ejecuta el script lanzador:
   ```bash
   ./iniciar.sh
   ```
4. El script realizará la misma comprobación e instalación automática del entorno `.venv` y lanzará la aplicación de escritorio.

---

## Guía de Uso de la Aplicación

### 1. Panel de Control (Dashboard)
Al iniciar la aplicación, serás recibido por el Dashboard principal que muestra estadísticas rápidas e indicadores de tu actividad.

> **[CAPTURA DE PANTALLA: Dashboard principal mostrando los paneles de Horas Pendientes, Total Facturado y Últimos Registros]**

*   **Horas Pendientes de Facturar**: El acumulado de tareas que has registrado y que aún no se han asociado a ninguna factura.
*   **Total Facturado**: La suma total neta de todas tus facturas emitidas.
*   **Acceso Rápido**: Visualización de los últimos registros de tiempo y facturas generadas.

### 2. Gestión de Clientes
Antes de empezar a registrar horas, es necesario registrar un cliente.
1. Haz clic en la sección **"Clientes"** del menú lateral.
2. Completa los datos en el formulario de la derecha (Nombre, NIF, Tarifa Horaria por defecto, Email, Dirección).
3. Haz clic en **"Guardar Cliente"**.
4. Puedes seleccionar cualquier cliente de la tabla de la izquierda para editar sus datos o eliminarlo.

> **[CAPTURA DE PANTALLA: Sección de Clientes con el listado en la izquierda y el formulario de añadir/editar en la derecha]**

### 3. Registro de Tiempos
Para imputar horas trabajadas a un cliente:
1. Haz clic en **"Registro y Facturación"** en el menú lateral.
2. En la pestaña superior, selecciona **"Registrar Tiempos"**.
3. Selecciona el cliente, introduce la fecha del trabajo, la cantidad de horas trabajadas (ej. `2.5`), una descripción de la tarea y notas internas (opcional).
4. Haz clic en **"Guardar Registro"**.

> **[CAPTURA DE PANTALLA: Formulario de Registro de Tiempos introduciendo horas trabajadas para un cliente específico]**

### 4. Generación de Facturas
1. En **"Registro y Facturación"**, ve a la pestaña **"Emitir Facturas"**.
2. Selecciona el cliente y define el rango de fechas de los trabajos a facturar.
3. El sistema te mostrará automáticamente todas las tareas pendientes de facturación de ese cliente en ese rango.
4. Selecciona el **Tipo de Factura**:
    *   **Por Horas**: Se calculará el total en función de las tareas seleccionadas en la lista inferior y la tarifa del cliente.
    *   **Por Proyecto**: Podrás ingresar un concepto libre y un importe neto preacordado de forma directa.
5. Selecciona mediante las casillas de verificación las tareas que deseas incluir en esta factura (las tareas seleccionadas quedarán marcadas en la base de datos como "facturadas" y no se volverán a mostrar).
6. Haz clic en **"Generar Factura (PDF)"**. El archivo se abrirá automáticamente tras crearse.

> **[CAPTURA DE PANTALLA: Interfaz de Facturación con la selección de tareas pendientes de cobro y opciones de IVA/IRPF]**

### 5. Configuración de Datos del Emisor
Es fundamental que rellenes tus propios datos fiscales antes de emitir tu primera factura real:
1. Dirígete a la pestaña de **"Configuración"** en la esquina inferior izquierda.
2. Completa tus datos fiscales de Autónomo (Nombre, NIF, Dirección, Email y Cuenta Bancaria para el cobro).
3. Indica el tipo de IVA por defecto (ej. `21.0`) y la retención del IRPF (ej. `15.0`).
4. Configura la carpeta de destino donde deseas guardar por defecto los PDFs de tus facturas. Si lo dejas en blanco, se guardarán en la carpeta `facturas_emitidas/` del proyecto.
5. Haz clic en **"Guardar Configuración"**.

> **[CAPTURA DE PANTALLA: Vista de Configuración del emisor con las tasas de impuestos y el IBAN de cobro]**

---

## Estructura del Proyecto

*   `iniciar.bat` y `iniciar.sh`: Lanzadores multiplataforma.
*   `initialize_project.py`: Script de configuración y sembrado de base de datos inicial.
*   `requirements.txt`: Dependencias requeridas del proyecto.
*   `pyproject.toml`: Metadatos del proyecto (versión v0.1.0).
*   `facturacion_app/`:
    *   `facturacion.db`: Archivo local de base de datos SQLite (se crea en la primera ejecución, no se sube a Git).
    *   `config/settings.json`: Configuración local del emisor (se crea en la primera ejecución, no se sube a Git).
    *   `src/`: Código fuente de la aplicación en Python (controladores, modelos, vistas e inicializadores).
    *   `templates/`: Plantillas HTML y hojas de estilo CSS para renderizar los PDFs de las facturas.
*   `facturas_emitidas/`: Carpeta local predeterminada para guardar los PDFs generados.

---

## Licencia

Este proyecto está bajo la Licencia [MIT](https://opensource.org/licenses/MIT). Eres libre de usarlo, modificarlo y distribuirlo para fines comerciales o privados.
