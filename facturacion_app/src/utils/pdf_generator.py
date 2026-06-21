import os
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
from xhtml2pdf import pisa
from src.models.invoice import Invoice
from src.models.client import Client
from src.models.time_log import TimeLog

# Determinar directorios base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "facturas_emitidas")

def ejecutar_generacion_pdf(invoice: Invoice, client: Client, logs: list[TimeLog]) -> str:
    """Genera un archivo PDF a partir del template HTML/CSS y los datos de facturación."""
    
    # 1. Cargar datos del emisor desde settings.json
    if not os.path.exists(SETTINGS_PATH):
        raise FileNotFoundError(
            "No se encontró el archivo de configuración. Por favor, configure primero los datos del emisor."
        )
        
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"El archivo de configuración settings.json está corrupto o mal formado: {e}")
        
    emisor = settings.get("emisor", {})
    if not emisor.get("nombre") or not emisor.get("nif"):
        raise ValueError("Los datos del emisor en la configuración no están completos (nombre y NIF son obligatorios).")

    # 2. Cargar el estilo CSS de la plantilla
    css_path = os.path.join(TEMPLATES_DIR, "invoice_style.css")
    if not os.path.exists(css_path):
        raise FileNotFoundError(f"No se encontró la hoja de estilos de factura en '{css_path}'")
        
    with open(css_path, "r", encoding="utf-8") as f:
        style_content = f.read()

    # 3. Inicializar Jinja2 con autoescape estricto
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    try:
        template = env.get_template("invoice_template.html")
    except Exception as e:
        raise RuntimeError(f"Error al cargar la plantilla HTML de la factura: {e}")

    # 4. Renderizar plantilla en memoria
    # Pasamos una lista de diccionarios para los logs de tiempo para asegurar compatibilidad
    logs_data = []
    for log in logs:
        logs_data.append({
            "date": log.date,
            "description": log.description,
            "hours": log.hours
        })

    rendered_html = template.render(
        invoice=invoice,
        client=client,
        logs=logs_data,
        emisor=emisor,
        style_content=style_content
    )

    # 5. Asegurar que existe el directorio de facturas emitidas
    ruta_personalizada = settings.get("ruta_facturas", "").strip()
    if ruta_personalizada:
        output_dir = os.path.normpath(ruta_personalizada)
    else:
        output_dir = os.path.join(os.path.dirname(BASE_DIR), "facturas_emitidas")

    # Si hay cliente y tiene un nombre, se organiza en una subcarpeta con el nombre del cliente
    if client and getattr(client, "name", None):
        client_name = client.name.strip()
        if client_name:
            # Sanitizar caracteres no permitidos en nombres de directorios (Windows: \ / : * ? " < > |)
            for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                client_name = client_name.replace(char, '_')
            client_name = client_name.strip()
            if client_name:
                output_dir = os.path.join(output_dir, client_name)

    os.makedirs(output_dir, exist_ok=True)
    
    # Crear un nombre de archivo limpio libre de caracteres problemáticos
    safe_number = invoice.invoice_number.replace("/", "_").replace("\\", "_").replace(" ", "_")
    pdf_filename = f"Factura_{safe_number}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    # 6. Ejecutar la conversión HTML -> PDF con xhtml2pdf
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
            src=rendered_html,
            dest=pdf_file,
            encoding="utf-8"
        )

    if pisa_status.err:
        # Si ocurre un error, intentamos eliminar el PDF potencialmente corrupto
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except OSError:
                pass
        raise RuntimeError("xhtml2pdf falló al renderizar el documento PDF.")

    return pdf_path


def ejecutar_generacion_informe_pdf(client: Client, logs: list[dict], start_date_str: str, end_date_str: str) -> str:
    """Genera un archivo PDF de informe de avances a partir de un template HTML/CSS y datos de tareas."""
    
    # 1. Cargar datos del emisor desde settings.json
    if not os.path.exists(SETTINGS_PATH):
        raise FileNotFoundError(
            "No se encontró el archivo de configuración. Por favor, configure primero los datos del emisor."
        )
        
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"El archivo de configuración settings.json está corrupto o mal formado: {e}")
        
    emisor = settings.get("emisor", {})
    if not emisor.get("nombre") or not emisor.get("nif"):
        raise ValueError("Los datos del emisor en la configuración no están completos (nombre y NIF son obligatorios).")

    # 2. Cargar el estilo CSS de la plantilla
    css_path = os.path.join(TEMPLATES_DIR, "report_style.css")
    if not os.path.exists(css_path):
        raise FileNotFoundError(f"No se encontró la hoja de estilos de informe en '{css_path}'")
        
    with open(css_path, "r", encoding="utf-8") as f:
        style_content = f.read()

    # 3. Inicializar Jinja2 con autoescape estricto
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    try:
        template = env.get_template("report_template.html")
    except Exception as e:
        raise RuntimeError(f"Error al cargar la plantilla HTML del informe: {e}")

    # 4. Renderizar plantilla en memoria
    logs_data = []
    total_hours = 0.0
    for log in logs:
        hours = log.get("hours", 0.0)
        total_hours += hours
        logs_data.append({
            "date": log.get("date"),
            "description": log.get("description"),
            "hours": hours,
            "notes": log.get("notes") or ""
        })

    # Calcular total de minutos para mostrar de forma amigable
    total_minutes = round(total_hours * 60)
    h_val = total_minutes // 60
    m_val = total_minutes % 60
    time_summary_str = f"{h_val}h {m_val}m" if h_val > 0 else f"{m_val}m"

    rendered_html = template.render(
        client=client,
        logs=logs_data,
        total_hours=total_hours,
        time_summary=time_summary_str,
        start_date=start_date_str,
        end_date=end_date_str,
        emisor=emisor,
        style_content=style_content
    )

    # 5. Asegurar que existe el directorio de informes
    ruta_personalizada = settings.get("ruta_informes", "").strip()
    if ruta_personalizada:
        output_dir = os.path.normpath(ruta_personalizada)
    else:
        output_dir = os.path.join(os.path.dirname(BASE_DIR), "informes")

    # Si hay cliente y tiene un nombre, se organiza en una subcarpeta con el nombre del cliente
    if client and getattr(client, "name", None):
        client_name = client.name.strip()
        if client_name:
            # Sanitizar caracteres no permitidos en nombres de directorios (Windows: \ / : * ? " < > |)
            for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                client_name = client_name.replace(char, '_')
            client_name = client_name.strip()
            if client_name:
                output_dir = os.path.join(output_dir, client_name)

    os.makedirs(output_dir, exist_ok=True)
    
    # Crear un nombre de archivo limpio basado en el tramo de días
    # Formato: Informe_2026-06-01_a_2026-06-15.pdf
    pdf_filename = f"Informe_{start_date_str}_a_{end_date_str}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    # 6. Ejecutar la conversión HTML -> PDF con xhtml2pdf
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(
            src=rendered_html,
            dest=pdf_file,
            encoding="utf-8"
        )

    if pisa_status.err:
        # Si ocurre un error, intentamos eliminar el PDF potencialmente corrupto
        if os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
            except OSError:
                pass
        raise RuntimeError("xhtml2pdf falló al renderizar el informe PDF.")

    return pdf_path
