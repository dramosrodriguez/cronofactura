import sqlite3
from src.database.db_manager import DatabaseManager

class Client:
    """Clase modelo para representar y operar sobre los Clientes."""
    
    def __init__(self, name: str, nif: str, hourly_rate: float, email: str, address: str, id: int = None, created_at: str = None):
        self.id = id
        self.name = name
        self.nif = nif
        self.hourly_rate = hourly_rate
        self.email = email
        self.address = address
        self.created_at = created_at

    @classmethod
    def from_row(cls, row):
        """Construye un objeto Client a partir de una fila de SQLite."""
        if not row:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            nif=row["nif"],
            hourly_rate=row["hourly_rate"],
            email=row["email"],
            address=row["address"],
            created_at=row["created_at"]
        )

    def save(self) -> int:
        """Guarda el cliente en la base de datos y retorna su id."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO clients (name, nif, hourly_rate, email, address)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.name, self.nif, self.hourly_rate, self.email, self.address)
            )
            conn.commit()
            self.id = cursor.lastrowid
            return self.id
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al guardar cliente: {e}")
        finally:
            conn.close()

    def update(self) -> bool:
        """Actualiza los datos del cliente en la base de datos."""
        if not self.id:
            raise ValueError("No se puede actualizar un cliente sin ID.")
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                UPDATE clients
                SET name = ?, nif = ?, hourly_rate = ?, email = ?, address = ?
                WHERE id = ?
                """,
                (self.name, self.nif, self.hourly_rate, self.email, self.address, self.id)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al actualizar cliente: {e}")
        finally:
            conn.close()

    def delete(self) -> bool:
        """Elimina el cliente de la base de datos (si no tiene facturas/tiempos asociados debido a RESTRICT)."""
        if not self.id:
            raise ValueError("No se puede eliminar un cliente sin ID.")
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM clients WHERE id = ?", (self.id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al eliminar cliente (posiblemente debido a restricciones de integridad): {e}")
        finally:
            conn.close()

    @classmethod
    def get_by_id(cls, client_id: int) -> 'Client':
        """Busca un cliente por su ID."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
            row = cursor.fetchone()
            return cls.from_row(row)
        finally:
            conn.close()

    @classmethod
    def get_all(cls) -> list['Client']:
        """Obtiene la lista de todos los clientes ordenados por nombre."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM clients ORDER BY name ASC")
            rows = cursor.fetchall()
            return [cls.from_row(row) for row in rows]
        finally:
            conn.close()

    @classmethod
    def nif_exists(cls, nif: str, exclude_id: int = None) -> bool:
        """Comprueba si ya existe un cliente con el NIF indicado."""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            if exclude_id:
                cursor.execute("SELECT COUNT(*) FROM clients WHERE nif = ? AND id != ?", (nif, exclude_id))
            else:
                cursor.execute("SELECT COUNT(*) FROM clients WHERE nif = ?", (nif,))
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            conn.close()
