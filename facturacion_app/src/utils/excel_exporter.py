import pandas as pd
from src.database.db_manager import DatabaseManager

class ExcelExporter:
    """Clase de utilidades para exportar históricos a formatos de hoja de cálculo (Excel/CSV) con Pandas."""

    @staticmethod
    def export_invoices(destination_path: str, file_format: str = "excel") -> None:
        """Exporta el histórico de facturas a Excel o CSV."""
        conn = DatabaseManager.get_connection()
        query = """
            SELECT 
                i.invoice_number AS [Número Factura],
                c.name AS [Cliente],
                c.nif AS [NIF Cliente],
                i.issue_date AS [Fecha Emisión],
                i.due_date AS [Fecha Vencimiento],
                i.billing_type AS [Tipo Cobro],
                i.project_concept AS [Concepto Proyecto],
                i.subtotal AS [Subtotal (€)],
                i.vat_rate AS [Tasa IVA (%)],
                i.vat_amount AS [Cuota IVA (€)],
                i.irpf_rate AS [Tasa IRPF (%)],
                i.irpf_amount AS [Cuota IRPF (€)],
                i.total AS [Total Facturado (€)],
                i.pdf_path AS [Ruta PDF]
            FROM invoices i
            JOIN clients c ON i.client_id = c.id
            ORDER BY i.issue_date DESC, i.id DESC
        """
        try:
            df = pd.read_sql_query(query, conn)
            if file_format.lower() == "excel":
                df.to_excel(destination_path, index=False)
            else:
                df.to_csv(destination_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise RuntimeError(f"Error al exportar histórico de facturas: {e}")
        finally:
            conn.close()

    @staticmethod
    def export_time_logs(destination_path: str, file_format: str = "excel") -> None:
        """Exporta el histórico de registros de tiempo a Excel o CSV."""
        conn = DatabaseManager.get_connection()
        query = """
            SELECT 
                t.date AS [Fecha],
                c.name AS [Cliente],
                c.nif AS [NIF Cliente],
                t.hours AS [Horas Trabajadas],
                t.description AS [Descripción],
                CASE 
                    WHEN t.invoice_id IS NULL THEN 'Pendiente'
                    ELSE 'Facturado (' || i.invoice_number || ')'
                END AS [Estado Facturación]
            FROM time_logs t
            JOIN clients c ON t.client_id = c.id
            LEFT JOIN invoices i ON t.invoice_id = i.id
            ORDER BY t.date DESC, t.id DESC
        """
        try:
            df = pd.read_sql_query(query, conn)
            if file_format.lower() == "excel":
                df.to_excel(destination_path, index=False)
            else:
                df.to_csv(destination_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise RuntimeError(f"Error al exportar histórico de tiempos: {e}")
        finally:
            conn.close()
