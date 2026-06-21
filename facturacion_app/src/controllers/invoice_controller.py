import os
import sqlite3
from datetime import datetime
from src.database.db_manager import DatabaseManager
from src.models.client import Client
from src.models.time_log import TimeLog
from src.models.invoice import Invoice
from src.utils.pdf_generator import ejecutar_generacion_pdf

class InvoiceController:
    """Controlador encargado de la lógica de negocio, consolidación y facturación transaccional."""

    @staticmethod
    def preview_invoice(client_id: int, start_date_str: str, end_date_str: str) -> dict:
        """Calcula una vista previa del subtotal y número de horas sin alterar la base de datos."""
        client = Client.get_by_id(client_id)
        if not client:
            raise ValueError("El cliente no existe.")

        logs = TimeLog.get_unbilled(client_id, start_date_str, end_date_str)
        if not logs:
            return {
                "total_hours": 0.0,
                "subtotal": 0.0,
                "logs": []
            }

        total_hours = sum(log.hours for log in logs)
        # El subtotal se calcula a partir de las horas del registro multiplicado por la tarifa del cliente
        subtotal = sum(log.hours * client.hourly_rate for log in logs)

        return {
            "total_hours": total_hours,
            "subtotal": subtotal,
            "logs": logs,
            "client_rate": client.hourly_rate
        }

    @staticmethod
    def create_invoice(invoice_number: str, client_id: int, start_date_str: str, end_date_str: str,
                       issue_date_str: str, due_date_str: str, vat_rate: float, irpf_rate: float,
                       billing_type: str = "horas", project_concept: str = None, custom_subtotal: float = None,
                       selected_log_ids: list[int] = None) -> Invoice:
        """Realiza la consolidación de tiempos, cálculos de impuestos y guarda la factura en una transacción atómica."""
        # Sanitizar entradas
        invoice_number = invoice_number.strip()
        if not invoice_number:
            raise ValueError("El número de factura es obligatorio.")

        # Validar si el número de factura ya existe
        if Invoice.invoice_number_exists(invoice_number):
            raise ValueError(f"El número de factura '{invoice_number}' ya está registrado.")

        client = Client.get_by_id(client_id)
        if not client:
            raise ValueError("El cliente especificado no existe.")

        # Validar si el cliente está completo
        is_client_complete = bool(
            client.name and client.name.strip() and
            client.nif and client.nif.strip() and not client.nif.startswith("PENDIENTE-") and
            client.email and client.email.strip() and
            client.address and client.address.strip() and
            client.hourly_rate > 0
        )
        if not is_client_complete:
            raise ValueError("No se puede generar la factura final para un cliente con datos incompletos.")

        # Validar fechas
        try:
            datetime.strptime(start_date_str, "%Y-%m-%d")
            datetime.strptime(end_date_str, "%Y-%m-%d")
            datetime.strptime(issue_date_str, "%Y-%m-%d")
            datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Los formatos de fecha deben ser YYYY-MM-DD.")

        if start_date_str > end_date_str:
            raise ValueError("La fecha de inicio de facturación no puede ser posterior a la fecha de fin.")

        if vat_rate < 0 or irpf_rate < 0:
            raise ValueError("Las tasas impositivas no pueden ser negativas.")

        # Recuperar registros de tiempo no facturados
        logs = TimeLog.get_unbilled(client_id, start_date_str, end_date_str)
        if selected_log_ids is not None:
            logs = [log for log in logs if log.id in selected_log_ids]

        if not logs:
            raise ValueError("No hay registros de tiempo seleccionados para facturar en este rango.")

        # Calcular valores financieros
        if billing_type == "proyecto" and custom_subtotal is not None:
            subtotal = custom_subtotal
        else:
            subtotal = sum(log.hours * client.hourly_rate for log in logs)

        vat_amount = subtotal * (vat_rate / 100.0)
        irpf_amount = subtotal * (irpf_rate / 100.0)
        total = subtotal + vat_amount - irpf_amount

        # Instanciar el objeto factura
        invoice = Invoice(
            invoice_number=invoice_number,
            client_id=client_id,
            issue_date=issue_date_str,
            due_date=due_date_str,
            vat_rate=vat_rate,
            irpf_rate=irpf_rate,
            subtotal=subtotal,
            vat_amount=vat_amount,
            irpf_amount=irpf_amount,
            total=total,
            billing_type=billing_type,
            project_concept=project_concept
        )

        # Iniciar transacción SQLite atómica para guardar factura y asociar logs
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        try:
            # En SQLite, con `with conn:` las operaciones se envuelven en una transacción y se hace commit de forma automática.
            with conn:
                # 1. Guardar factura pasándole el cursor actual
                invoice.save(conn)
                
                # 2. Asociar los logs de tiempo actualizando su invoice_id
                log_ids = [log.id for log in logs]
                # Preparar la query de actualización con placeholders parametrizados para los IDs
                placeholders = ",".join("?" for _ in log_ids)
                query = f"UPDATE time_logs SET invoice_id = ? WHERE id IN ({placeholders})"
                cursor.execute(query, [invoice.id] + log_ids)
                
        except sqlite3.Error as e:
            raise RuntimeError(f"Fallo en la transacción de base de datos: {e}")
        finally:
            conn.close()

        # Generar el PDF y guardar la ruta
        try:
            pdf_path = ejecutar_generacion_pdf(invoice, client, logs)
            invoice.update_pdf_path(pdf_path)
        except Exception as e:
            # Aunque falle el PDF, la factura ya se guardó en la DB. Lanzamos advertencia o error del PDF
            raise RuntimeError(f"Factura creada con éxito en la base de datos, pero falló la generación del PDF: {e}")

        return invoice

    @staticmethod
    def list_invoices() -> list[dict]:
        """Obtiene la lista de todas las facturas emitidas con su cliente asociado."""
        return Invoice.get_extended_invoices()

    @staticmethod
    def get_invoice_details(invoice_id: int) -> dict:
        """Obtiene la factura, cliente y logs de tiempo asociados para visualización o regeneración."""
        invoice = Invoice.get_by_id(invoice_id)
        if not invoice:
            raise ValueError("La factura no existe.")

        client = Client.get_by_id(invoice.client_id)
        logs = TimeLog.get_by_invoice(invoice_id)

        return {
            "invoice": invoice,
            "client": client,
            "logs": logs
        }

    @staticmethod
    def delete_invoice(invoice_id: int) -> bool:
        """Elimina una factura de la base de datos por su ID."""
        invoice = Invoice.get_by_id(invoice_id)
        if not invoice:
            raise ValueError("La factura especificada no existe.")
        return invoice.delete()
