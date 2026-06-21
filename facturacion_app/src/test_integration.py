import os
import sys

# BASE_DIR es el directorio raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Añadir el directorio raíz de la aplicación (facturacion_app) al path de python
sys.path.append(os.path.join(BASE_DIR, "facturacion_app"))

import json
import src.database.db_manager as db_manager
from src.database.db_manager import DatabaseManager
from src.controllers.client_controller import ClientController
from src.controllers.time_controller import TimeController
from src.controllers.invoice_controller import InvoiceController
from src.utils.excel_exporter import ExcelExporter
from src.models.time_log import TimeLog

# Sobrescribir la ruta de la base de datos para pruebas
db_manager.DB_PATH = os.path.join(BASE_DIR, "test_facturacion.db")

def run_tests():
    print("--- INICIANDO PRUEBAS DE INTEGRACIÓN ---")
    
    # Asegurar un entorno limpio eliminando la DB de prueba previa
    if os.path.exists(db_manager.DB_PATH):
        try:
            os.remove(db_manager.DB_PATH)
        except Exception:
            pass
    for ext in ["-wal", "-journal", "-shm"]:
        p = db_manager.DB_PATH + ext
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

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

    # Validar generación del informe de avances PDF
    print("\n[Opcional] Validando generación de informe de avances (PDF)...")
    from src.utils.pdf_generator import ejecutar_generacion_informe_pdf
    
    report_logs = TimeController.list_logs()
    # filtrar solo para nuestro cliente de prueba
    client_logs = [log for log in report_logs if log["client_name"] == client.name]
    
    report_pdf_path = ejecutar_generacion_informe_pdf(client, client_logs, "2026-06-01", "2026-06-30")
    print(f"Informe PDF generado en: {report_pdf_path}")
    if not os.path.exists(report_pdf_path):
        raise ValueError("Error: el archivo PDF de informe de avances no fue creado.")
    
    # Limpiar informe
    try:
        os.remove(report_pdf_path)
        # eliminar subcarpeta del cliente si queda vacía
        os.rmdir(os.path.dirname(report_pdf_path))
    except Exception:
        pass
    
    print("\n--- INICIANDO PRUEBAS DE ELIMINACIÓN ---")
    
    # 6. Probar eliminación de factura
    print("Eliminando la factura por horas...")
    invoice_id_to_delete = invoice_hours.id
    success_delete_invoice = InvoiceController.delete_invoice(invoice_id_to_delete)
    print(f"Resultado de eliminar factura {invoice_hours.invoice_number}: {success_delete_invoice}")
    if not success_delete_invoice:
        raise ValueError("Error: no se pudo eliminar la factura de la base de datos.")
    
    # Comprobar que la factura ya no existe
    try:
        InvoiceController.get_invoice_details(invoice_id_to_delete)
        raise ValueError("Error: la factura eliminada sigue existiendo en el sistema.")
    except ValueError as e:
        if "La factura no existe" in str(e):
            print("Confirmado: la factura ya no existe en la base de datos.")
        else:
            raise e

    # Comprobar que las tareas asociadas (como log1) ahora tienen invoice_id = NULL
    # Recuperamos todos los logs usando get_all
    all_current_logs = TimeLog.get_all()
    log1_after_delete = next((l for l in all_current_logs if l.id == log1.id), None)
    if not log1_after_delete:
        raise ValueError("Error: la tarea log1 se eliminó, cuando solo debía desvincularse de la factura.")
    
    print(f"Estado de log1 tras eliminar la factura: invoice_id = {log1_after_delete.invoice_id} (Debería ser None)")
    if log1_after_delete.invoice_id is not None:
        raise ValueError("Error: la tarea no se desvinculó de la factura (invoice_id no es NULL).")
    else:
        print("¡Verificación de desvinculación exitosa! La tarea volvió a quedar pendiente.")

    # 7. Probar eliminación de tarea (log2)
    print("\nEliminando la tarea log2...")
    success_delete_log = TimeController.delete_log(log2.id)
    print(f"Resultado de eliminar tarea: {success_delete_log}")
    if not success_delete_log:
        raise ValueError("Error: no se pudo eliminar la tarea.")

    # Verificar que log2 ya no existe
    all_current_logs_after = TimeLog.get_all()
    log2_exists = any(l.id == log2.id for l in all_current_logs_after)
    print(f"¿Existe la tarea log2 en la base de datos?: {log2_exists} (Debería ser False)")
    if log2_exists:
        raise ValueError("Error: la tarea log2 no se eliminó correctamente de la base de datos.")
    # 8. Probar actualización de tareas (update_log)
    print("\n[8] Probando actualización de tareas...")
    test_update_log = TimeController.create_log(client.id, "2026-06-14", 2.0, "Tarea para actualizar")
    print(f"Log creado para actualizar: {test_update_log.description} | {test_update_log.hours}h")
    
    # Intentar actualización exitosa
    success_update = TimeController.update_log(
        log_id=test_update_log.id,
        client_id=client.id,
        date_str="2026-06-15",
        hours=3.5,
        description="Tarea actualizada con éxito",
        notes="Nueva nota interna"
    )
    print(f"Resultado de la actualización: {success_update}")
    if not success_update:
        raise ValueError("Error: la tarea no se pudo actualizar.")
        
    # Verificar cambios en BD
    updated_log = TimeLog.get_by_id(test_update_log.id)
    print(f"Detalles actualizados: Desc={updated_log.description}, Horas={updated_log.hours}, Fecha={updated_log.date}, Notes={updated_log.notes}")
    if updated_log.description != "Tarea actualizada con éxito" or updated_log.hours != 3.5 or updated_log.date != "2026-06-15" or updated_log.notes != "Nueva nota interna":
        raise ValueError("Error: los datos de la tarea en base de datos no coinciden con la actualización.")

    # Vincular a una nueva factura
    invoice_num_test = f"F-TST-{int(os.getpid())}"
    invoice_test = InvoiceController.create_invoice(
        invoice_number=invoice_num_test,
        client_id=client.id,
        start_date_str="2026-06-01",
        end_date_str="2026-06-30",
        issue_date_str="2026-06-14",
        due_date_str="2026-07-14",
        vat_rate=21.0,
        irpf_rate=15.0,
        billing_type="horas",
        selected_log_ids=[updated_log.id]
    )
    print(f"Log vinculado a la factura: {invoice_test.invoice_number}")
    
    # Intentar actualización de una tarea facturada (debe lanzar ValueError)
    try:
        TimeController.update_log(
            log_id=updated_log.id,
            client_id=client.id,
            date_str="2026-06-16",
            hours=4.0,
            description="Intento de actualizar tarea facturada"
        )
        raise ValueError("Error: se permitió la actualización de una tarea ya facturada.")
    except ValueError as e:
        print(f"Excepción controlada correctamente al actualizar tarea facturada: {e}")

    # 9. Probando cliente incompleto y bloqueo de facturación final
    print("\n[9] Probando cliente incompleto y bloqueo de facturación final...")
    try:
        incomplete_client = ClientController.create_client(
            name="Cliente Incompleto",
            nif="",           # Debería generar un NIF PENDIENTE-xxx
            hourly_rate=0.0,
            email="",
            address=""
        )
        print(f"Cliente incompleto creado con éxito: {incomplete_client.name} (NIF auto: {incomplete_client.nif})")
        if not incomplete_client.nif.startswith("PENDIENTE-"):
            raise ValueError("Error: El NIF temporal no se generó con el formato correcto.")
    except Exception as e:
        raise ValueError(f"Error: no se pudo crear un cliente incompleto: {e}")

    # Intentar generar factura para el cliente incompleto (debe lanzar ValueError)
    try:
        incomplete_log = TimeController.create_log(
            client_id=incomplete_client.id,
            date_str="2026-06-15",
            hours=2.0,
            description="Trabajo preliminar"
        )
        
        InvoiceController.create_invoice(
            invoice_number=f"F-INC-{int(os.getpid())}",
            client_id=incomplete_client.id,
            start_date_str="2026-06-01",
            end_date_str="2026-06-30",
            issue_date_str="2026-06-15",
            due_date_str="2026-07-15",
            vat_rate=21.0,
            irpf_rate=15.0,
            billing_type="horas",
            selected_log_ids=[incomplete_log.id]
        )
        raise ValueError("Error: se permitió la creación de una factura para un cliente incompleto.")
    except ValueError as e:
        if "No se puede generar la factura final para un cliente con datos incompletos" in str(e):
            print(f"Excepción controlada correctamente al facturar cliente incompleto: {e}")
        else:
            raise e

    print("\n--- ¡TODAS LAS PRUEBAS BACKEND Y DE ELIMINACIÓN PASARON CON ÉXITO! ---")
    
    # Limpiar base de datos al finalizar
    if os.path.exists(db_manager.DB_PATH):
        try:
            os.remove(db_manager.DB_PATH)
        except Exception:
            pass
    for ext in ["-wal", "-journal", "-shm"]:
        p = db_manager.DB_PATH + ext
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

if __name__ == "__main__":
    run_tests()

