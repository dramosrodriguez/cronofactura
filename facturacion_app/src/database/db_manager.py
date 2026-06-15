import os
import sqlite3

# Determinar la ruta absoluta del archivo de la base de datos en la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "facturacion.db")

class DatabaseManager:
    """Clase encargada de gestionar la conexión a la base de datos SQLite,
    aplicar configuraciones de rendimiento y seguridad, y ejecutar migraciones básicas.
    """
    
    @staticmethod
    def get_connection():
        """Obtiene una conexión a la base de datos activando claves foráneas y modo WAL."""
        db_exists = os.path.exists(DB_PATH)
        
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acceder a los resultados por nombre de columna
        
        # Activar el control estricto de claves foráneas
        conn.execute("PRAGMA foreign_keys = ON;")
        # Activar modo WAL (Write-Ahead Logging) para rendimiento concurrente
        conn.execute("PRAGMA journal_mode = WAL;")
        
        if not db_exists:
            # Si la base de datos es nueva, podemos realizar inicializaciones adicionales si es necesario
            pass
            
        return conn

    @classmethod
    def init_db(cls):
        """Inicializa las tablas y los índices de la base de datos si no existen."""
        # Asegurarse de que el directorio padre existe
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        conn = cls.get_connection()
        cursor = conn.cursor()
        
        try:
            # Crear tabla clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    nif TEXT NOT NULL UNIQUE,
                    hourly_rate REAL NOT NULL CHECK(hourly_rate >= 0),
                    email TEXT NOT NULL,
                    address TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now', 'localtime'))
                );
            """)
            
            # Crear tabla facturas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT NOT NULL UNIQUE,
                    client_id INTEGER NOT NULL,
                    issue_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    vat_rate REAL NOT NULL CHECK(vat_rate >= 0),
                    irpf_rate REAL NOT NULL CHECK(irpf_rate >= 0),
                    subtotal REAL NOT NULL CHECK(subtotal >= 0),
                    vat_amount REAL NOT NULL CHECK(vat_amount >= 0),
                    irpf_amount REAL NOT NULL CHECK(irpf_amount >= 0),
                    total REAL NOT NULL CHECK(total >= 0),
                    pdf_path TEXT,
                    billing_type TEXT DEFAULT 'horas',
                    project_concept TEXT DEFAULT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT
                );
            """)
            
            # Crear tabla registros de tiempo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    hours REAL NOT NULL CHECK(hours > 0),
                    description TEXT NOT NULL,
                    notes TEXT DEFAULT NULL,
                    invoice_id INTEGER DEFAULT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE SET NULL
                );
            """)
            
            # Ejecutar migración para base de datos existente si fuera necesario
            try:
                cursor.execute("ALTER TABLE time_logs ADD COLUMN notes TEXT DEFAULT NULL;")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE invoices ADD COLUMN billing_type TEXT DEFAULT 'horas';")
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("ALTER TABLE invoices ADD COLUMN project_concept TEXT DEFAULT NULL;")
            except sqlite3.OperationalError:
                pass
            
            # Crear índices para acelerar búsquedas y asegurar integridad referencial
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_logs_client_date ON time_logs(client_id, date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_time_logs_invoice ON time_logs(invoice_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_issue_date ON invoices(issue_date);")
            
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise RuntimeError(f"Error al inicializar la base de datos: {e}")
        finally:
            conn.close()
