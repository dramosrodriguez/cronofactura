import sqlite3
from src.database.db_manager import DatabaseManager

class Invoice:
    """Clase modelo para representar y operar sobre las Facturas."""

    def __init__(self, invoice_number: str, client_id: int, issue_date: str, due_date: str,
                 vat_rate: float, irpf_rate: float, subtotal: float, vat_amount: float,
                 irpf_amount: float, total: float, pdf_path: str = None, id: int = None,
                 billing_type: str = "horas", project_concept: str = None):
        self.id = id
        self.invoice_number = invoice_number
        self.client_id = client_id
        self.issue_date = issue_date
        self.due_date = due_date
        self.vat_rate = vat_rate
        self.irpf_rate = irpf_rate
        self.subtotal = subtotal
        self.vat_amount = vat_amount
        self.irpf_amount = irpf_amount
        self.total = total
        self.pdf_path = pdf_path
        self.billing_type = billing_type
        self.project_concept = project_concept

    @classmethod
    def from_row(cls, row):
        """Construye un objeto Invoice a partir de una fila de SQLite."""
        if not row:
            return None
        return cls(
            id=row["id"],
            invoice_number=row["invoice_number"],
            client_id=row["client_id"],
            issue_date=row["issue_date"],
            due_date=row["due_date"],
            vat_rate=row["vat_rate"],
            irpf_rate=row["irpf_rate"],
            subtotal=row["subtotal"],
            vat_amount=row["vat_amount"],
            irpf_amount=row["irpf_amount"],
            total=row["total"],
            pdf_path=row["pdf_path"],
            billing_type=row["billing_type"] if "billing_type" in row.keys() else "horas",
            project_concept=row["project_concept"] if "project_concept" in row.keys() else None
        )

    def save(self, conn=None) -> int:
        """Guarda la factura en la base de datos.
        Acepta una conexión externa opcional para participar en una transacción.
        """
        local_conn = False
        if conn is None:
            conn = DatabaseManager.get_connection()
            local_conn = True
            
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO invoices (
                    invoice_number, client_id, issue_date, due_date,
                    vat_rate, irpf_rate, subtotal, vat_amount, irpf_amount, total, pdf_path,
                    billing_type, project_concept
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.invoice_number, self.client_id, self.issue_date, self.due_date,
                    self.vat_rate, self.irpf_rate, self.subtotal, self.vat_amount,
                    self.irpf_amount, self.total, self.pdf_path, self.billing_type, self.project_concept
                )
            )
            if local_conn:
                conn.commit()
            self.id = cursor.lastrowid
            return self.id
        except sqlite3.Error as e:
            if local_conn:
                conn.rollback()
            raise RuntimeError(f"Error al guardar la factura: {e}")
        finally:
            if local_conn:
                conn.close()

    def update_pdf_path(self, pdf_path: str) -> bool:
        """Actualiza la ruta del PDF una vez generado."""
        if not self.id:
            raise ValueError("No se puede actualizar el PDF de una factura sin ID.")
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "UPDATE invoices SET pdf_path = ? WHERE id = ?",
                (pdf_path, self.id)
            )
            conn.commit()
            self.pdf_path = pdf_path
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al actualizar la ruta del PDF: {e}")
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, invoice_id: int) -> 'Invoice':
        """Busca una factura por su ID."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
            row = cursor.fetchone()
            return cls.from_row(row)
        finally:
            conn.close()

    @classmethod
    def get_all(cls) -> list['Invoice']:
        """Obtiene todas las facturas ordenadas por fecha de emisión descendente."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM invoices ORDER BY issue_date DESC, id DESC")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def get_extended_invoices(cls) -> list[dict]:
        """Obtiene las facturas con el nombre de su cliente."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT i.*, c.name as client_name 
                FROM invoices i
                JOIN clients c ON i.client_id = c.id
                ORDER BY i.issue_date DESC, i.id DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def invoice_number_exists(cls, invoice_number: str) -> bool:
        """Verifica si un número de factura ya existe."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM invoices WHERE invoice_number = ?", (invoice_number,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()

    @classmethod
    def get_statistics(cls) -> dict:
        """Obtiene estadísticas globales de facturación para el dashboard."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            # Total facturado
            cursor.execute("SELECT SUM(total), SUM(subtotal) FROM invoices")
            sum_total, sum_subtotal = cursor.fetchone()
            sum_total = sum_total if sum_total else 0.0
            sum_subtotal = sum_subtotal if sum_subtotal else 0.0

            # Número de facturas
            cursor.execute("SELECT COUNT(*) FROM invoices")
            count_invoices = cursor.fetchone()[0]

            # Facturación mensual (últimos 12 meses)
            cursor.execute(
                """
                SELECT strftime('%Y-%m', issue_date) as month, SUM(total) as monthly_total 
                FROM invoices 
                GROUP BY month 
                ORDER BY month DESC 
                LIMIT 12
                """
            )
            monthly_data = {row["month"]: row["monthly_total"] for row in cursor.fetchall()}

            return {
                "total_facturado": sum_total,
                "subtotal_facturado": sum_subtotal,
                "numero_facturas": count_invoices,
                "facturacion_mensual": monthly_data
            }
        finally:
            conn.close()
