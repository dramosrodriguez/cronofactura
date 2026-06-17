import sqlite3
from src.database.db_manager import DatabaseManager

class TimeLog:
    """Clase modelo para representar y operar sobre los Registros de Tiempo (horas)."""

    def __init__(self, client_id: int, date: str, hours: float, description: str, notes: str = None, invoice_id: int = None, id: int = None):
        self.id = id
        self.client_id = client_id
        self.date = date
        self.hours = hours
        self.description = description
        self.notes = notes
        self.invoice_id = invoice_id

    @classmethod
    def from_row(cls, row):
        """Construye un objeto TimeLog a partir de una fila de SQLite."""
        if not row:
            return None
        return cls(
            id=row["id"],
            client_id=row["client_id"],
            date=row["date"],
            hours=row["hours"],
            description=row["description"],
            notes=row["notes"] if "notes" in row.keys() else None,
            invoice_id=row["invoice_id"]
        )

    @classmethod
    def get_by_id(cls, log_id: int) -> 'TimeLog':
        """Obtiene un registro de tiempo por su ID."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM time_logs WHERE id = ?", (log_id,))
            row = cursor.fetchone()
            return cls.from_row(row) if row else None
        finally:
            conn.close()

    def save(self) -> int:
        """Guarda el registro de tiempo en la base de datos."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO time_logs (client_id, date, hours, description, notes, invoice_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (self.client_id, self.date, self.hours, self.description, self.notes, self.invoice_id)
            )
            conn.commit()
            self.id = cursor.lastrowid
            return self.id
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al guardar el registro de tiempo: {e}")
        finally:
            conn.close()

    def update(self) -> bool:
        """Actualiza el registro de tiempo en la base de datos."""
        if not self.id:
            raise ValueError("No se puede actualizar un registro sin ID.")
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE time_logs
                SET client_id = ?, date = ?, hours = ?, description = ?, notes = ?, invoice_id = ?
                WHERE id = ?
                """,
                (self.client_id, self.date, self.hours, self.description, self.notes, self.invoice_id, self.id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al actualizar el registro de tiempo: {e}")
        finally:
            conn.close()

    def delete(self) -> bool:
        """Elimina el registro de tiempo."""
        if not self.id:
            raise ValueError("No se puede eliminar un registro sin ID.")
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM time_logs WHERE id = ?", (self.id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al eliminar el registro de tiempo: {e}")
        finally:
            conn.close()

    @classmethod
    def get_all(cls) -> list['TimeLog']:
        """Obtiene todos los registros de tiempo, ordenados por fecha descendente."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM time_logs ORDER BY date DESC, id DESC")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def get_unbilled(cls, client_id: int, start_date: str, end_date: str) -> list['TimeLog']:
        """Obtiene los registros de tiempo no facturados (invoice_id IS NULL) de un cliente en un rango de fechas."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM time_logs
                WHERE client_id = ? AND date BETWEEN ? AND ? AND invoice_id IS NULL
                ORDER BY date ASC, id ASC
                """,
                (client_id, start_date, end_date)
            )
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def get_by_invoice(cls, invoice_id: int) -> list['TimeLog']:
        """Obtiene los registros de tiempo asociados a una factura."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT * FROM time_logs
                WHERE invoice_id = ?
                ORDER BY date ASC
                """,
                (invoice_id,)
            )
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]
        finally:
            conn.close()
            
    @classmethod
    def get_extended_logs(cls) -> list[dict]:
        """Obtiene todos los registros de tiempo con el nombre del cliente asociado."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                SELECT t.id, t.client_id, c.name as client_name, t.date, t.hours, t.description, t.notes, t.invoice_id
                FROM time_logs t
                JOIN clients c ON t.client_id = c.id
                ORDER BY t.date DESC, t.id DESC
                """
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
