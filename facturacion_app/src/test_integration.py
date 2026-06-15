import os
import sys

# BASE_DIR es el directorio raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Añadir el directorio raíz de la aplicación (facturacion_app) al path de python
sys.path.append(os.path.join(BASE_DIR, "facturacion_app"))

import json
from src.database.db_manager import DatabaseManager
from src.controllers.client_controller import ClientController
from src.controllers.time_controller import TimeController
from src.controllers.invoice_controller import InvoiceController
from src.utils.excel_exporter import ExcelExporter
from src.models.time_log import TimeLog

def run_tests():
    print("--- INICIANDO PRUEBAS DE INTEGRACIÓN ---")
    
    # 1. Verificar Inicialización de DB
    print("\n[1/5] Inicializando Base de Datos...")
    DatabaseManager.init_db()
    print("Base de datos y tablas creadas exitosamente.")
    
    # 2. Verificar archivo de configuración atómica
    print("\n[2/5] Verificando Configuración (settings.json)...")
    settings_dir = os.path.join(BASE_DIR, "facturacion_app", "config")
    settings_path = os.path.join(settings_dir, "settings.json")
    
    # Asegurar que existe el archivo para evitar fallos de PDF
    os.makedirs(settings_dir, exist_ok=True)
    test_config = {
        "emisor": {
            "nombre": "Prueba Autónomo S.L.",
            "nif": "B12345678",
            "direccion": "Calle de las Pruebas 10, Madrid",
            "email": "test@autonomo.com",
            "cuenta_bancaria": "ES91 2100 0418 4502 0005 4321"
        },
        "impuestos_defecto": {
            "iva_porcentaje": 21.0,
            "irpf_porcentaje": 15.0
        },
        "ruta_facturas": ""
    }
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(test_config, f, indent=2)
    print("Archivo config/settings.json inicializado.")

    # 3. Registrar Cliente de Prueba
    print("\n[3/5] Creando Cliente de Prueba...")
    try:
        # Intentar crear
        client = ClientController.create_client(
            name="Cliente de Prueba S.A.",
            nif="A87654321",
            hourly_rate=30.0,
            email="contacto@clienteprueba.com",
            address="Avenida Comercial 50, Barcelona"
        )
        print(f"Cliente creado: {client.name} (ID: {client.id}) con tarifa de {client.hourly_rate} €/h.")
    except Exception as e:
        print(f"ERROR al crear cliente (puede ser que ya exista): {e}")
        # Recuperar clientes existentes y tomar el primero
        clients = ClientController.list_clients()
        if not clients:
            raise RuntimeError("Fallo crítico: no hay clientes de prueba disponibles.")
        client = clients[0]
        print(f"Usando cliente existente: {client.name} (ID: {client.id})")

    # 4. Registrar logs de tiempo no facturados
    print("\n[4/5] Registrando Logs de Tiempo...")
    log_date = "2026-06-14"
    log1 = TimeController.create_log(client.id, log_date, 5.0, "Desarrollo de módulos core backend", notes="Nota interna oculta de prueba")
    log2 = TimeController.create_log(client.id, log_date, 3.5, "Maquetación CSS de facturas y UI")
    print(f"Logs de tiempo registrados: 5.0 h y 3.5 h (Total: 8.5 h).")

    # 5. Generar Facturas (Horas y Proyecto con Selección)
    print("\n[5/5] Consolidando Horas y Generando Facturas con Selección...")
    
    # --- FACTURA 1: POR HORAS (Seleccionando solo log1) ---
    invoice_num_hours = f"F-HRS-{int(os.getpid())}"
    invoice_hours = InvoiceController.create_invoice(
        invoice_number=invoice_num_hours,
        client_id=client.id,
        start_date_str="2026-06-01",
        end_date_str="2026-06-30",
        issue_date_str="2026-06-14",
        due_date_str="2026-07-14",
        vat_rate=21.0,
        irpf_rate=15.0,
        billing_type="horas",
        selected_log_ids=[log1.id]  # Solo seleccionamos la primera tarea
    )
    
    print("\n--- FACTURA POR HORAS EMITIDA EXITOSAMENTE ---")
    print(f"Número de Factura: {invoice_hours.invoice_number}")
    print(f"Subtotal: {invoice_hours.subtotal:.2f} € (Debería ser 150.00 € por 5.0h a 30€/h)")
    print(f"Cuota IVA (21%): {invoice_hours.vat_amount:.2f} €")
    print(f"Cuota IRPF (15%): {invoice_hours.irpf_amount:.2f} €")
    print(f"Total Neto: {invoice_hours.total:.2f} €")
    print(f"Tipo Cobro: {invoice_hours.billing_type}")
    print(f"Archivo PDF guardado en: {invoice_hours.pdf_path}")
    
    # Registrar nuevos logs de tiempo para la factura por proyecto
    print("\nRegistrando más logs para factura por Proyecto...")
    log3 = TimeController.create_log(client.id, log_date, 4.0, "Desarrollo de API de integración de pasarela")
    log4 = TimeController.create_log(client.id, log_date, 2.0, "Revisión final de seguridad y refactorización")
    print(f"Logs de tiempo registrados: 4.0 h y 2.0 h.")

    # --- FACTURA 2: POR PROYECTO (Seleccionando solo log3 y log4, dejando log2 pendiente) ---
    invoice_num_proj = f"F-PRJ-{int(os.getpid())}"
    invoice_project = InvoiceController.create_invoice(
        invoice_number=invoice_num_proj,
        client_id=client.id,
        start_date_str="2026-06-01",
        end_date_str="2026-06-30",
        issue_date_str="2026-06-14",
        due_date_str="2026-07-14",
        vat_rate=21.0,
        irpf_rate=15.0,
        billing_type="proyecto",
        project_concept="Desarrollo de API y Módulo de Integración de Pasarela",
        custom_subtotal=450.00,
        selected_log_ids=[log3.id, log4.id]  # Solo seleccionamos logs 3 y 4
    )
    
    print("\n--- FACTURA POR PROYECTO EMITIDA EXITOSAMENTE ---")
    print(f"Número de Factura: {invoice_project.invoice_number}")
    print(f"Concepto Proyecto: {invoice_project.project_concept}")
    print(f"Subtotal Personalizado: {invoice_project.subtotal:.2f} €")
    print(f"Cuota IVA (21%): {invoice_project.vat_amount:.2f} €")
    print(f"Cuota IRPF (15%): {invoice_project.irpf_amount:.2f} €")
    print(f"Total Neto: {invoice_project.total:.2f} €")
    print(f"Tipo Cobro: {invoice_project.billing_type}")
    print(f"Archivo PDF guardado en: {invoice_project.pdf_path}")

    # Validar que los logs de tiempo quedaron asignados
    details_hours = InvoiceController.get_invoice_details(invoice_hours.id)
    details_proj = InvoiceController.get_invoice_details(invoice_project.id)
    print(f"\nLogs vinculados en DB (Horas): {len(details_hours['logs'])} registros (Debería ser 1).")
    print(f"Logs vinculados en DB (Proyecto): {len(details_proj['logs'])} registros (Debería ser 2).")

    # Validar que log2 sigue sin facturar (pendiente)
    unbilled_logs = TimeLog.get_unbilled(client.id, "2026-06-01", "2026-06-30")
    print(f"Logs que permanecen sin facturar (pendientes): {len(unbilled_logs)} (Debería ser 1, log2 de 3.5h).")
    if len(unbilled_logs) == 1 and unbilled_logs[0].id == log2.id:
        print("¡Verificación de tareas pendientes exitosa! log2 permanece sin facturar.")
    else:
        raise ValueError("Error: las tareas pendientes no se gestionaron correctamente.")
    
    # Exportaciones de prueba
    print("\n[Opcional] Validando utilidades de exportación...")
    excel_path = os.path.join(BASE_DIR, "facturas_emitidas", "Prueba_Exportacion_Facturas.xlsx")
    csv_path = os.path.join(BASE_DIR, "facturas_emitidas", "Prueba_Exportacion_Tiempos.csv")
    
    ExcelExporter.export_invoices(excel_path, "excel")
    ExcelExporter.export_time_logs(csv_path, "csv")
    
    print(f"Exportaciones completadas con éxito:")
    print(f" - Excel Facturas: {excel_path}")
    print(f" - CSV Registro de Tiempos: {csv_path}")
    
    print("\n--- ¡TODAS LAS PRUEBAS BACKEND PASARON CON ÉXITO! ---")

if __name__ == "__main__":
    run_tests()
