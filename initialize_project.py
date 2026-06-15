import os
import sys
import json

# Configurar el path para poder importar desde el directorio de la aplicación
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "facturacion_app")
sys.path.append(APP_DIR)

from src.database.db_manager import DatabaseManager

def main():
    print("=== INICIALIZANDO EL PROYECTO ===")

    # 1. Crear configuración settings.json con datos genéricos si no existe
    config_dir = os.path.join(APP_DIR, "config")
    os.makedirs(config_dir, exist_ok=True)
    settings_path = os.path.join(config_dir, "settings.json")

    if not os.path.exists(settings_path):
        print("Creando archivo de configuración predeterminado settings.json...")
        default_config = {
            "emisor": {
                "nombre": "Autónomo Ejemplo S.L.",
                "nif": "B00000000",
                "direccion": "Calle Falsa 123, 1º Izquierda, Madrid",
                "email": "contacto@autonomoejemplo.com",
                "cuenta_bancaria": "ES00 0000 0000 0000 0000 0000"
            },
            "impuestos_defecto": {
                "iva_porcentaje": 21.0,
                "irpf_porcentaje": 15.0
            },
            "ruta_facturas": ""
        }
        try:
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print("Archivo settings.json creado correctamente con datos genéricos.")
        except Exception as e:
            print(f"Error al crear settings.json: {e}", file=sys.stderr)
    else:
        print("El archivo settings.json ya existe. No se modificará.")

    # 2. Inicializar base de datos y crear tablas
    print("Inicializando base de datos SQLite...")
    try:
        DatabaseManager.init_db()
        print("Base de datos y tablas verificadas/creadas con éxito.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Insertar datos genéricos de prueba si la base de datos está vacía
    conn = None
    try:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # Comprobar si hay clientes
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]
        
        if client_count == 0:
            print("La base de datos está vacía. Insertando datos genéricos de prueba...")
            
            # Insertar cliente genérico
            cursor.execute("""
                INSERT INTO clients (name, nif, hourly_rate, email, address)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Cliente de Prueba S.A.",
                "A87654321",
                35.0,
                "contacto@clienteprueba.com",
                "Avenida Diagonal 450, Barcelona"
            ))
            client_id = cursor.lastrowid
            
            # Insertar algunos registros de tiempo de ejemplo (uno del mes pasado y dos de hoy)
            cursor.execute("""
                INSERT INTO time_logs (client_id, date, hours, description, notes)
                VALUES (?, date('now', '-1 day'), ?, ?, ?)
            """, (
                client_id,
                4.5,
                "Desarrollo e integración de API REST para el cliente",
                "Nota: Fase inicial completada y probada"
            ))
            
            cursor.execute("""
                INSERT INTO time_logs (client_id, date, hours, description, notes)
                VALUES (?, date('now'), ?, ?, ?)
            """, (
                client_id,
                3.0,
                "Maquetación y diseño responsive de interfaz de facturación",
                "Nota: Usando componentes CustomTkinter"
            ))
            
            cursor.execute("""
                INSERT INTO time_logs (client_id, date, hours, description, notes)
                VALUES (?, date('now'), ?, ?, ?)
            """, (
                client_id,
                2.5,
                "Reunión de planificación de entregas e hitos de soporte",
                "Nota: Acordado segundo sprint del proyecto"
            ))
            
            conn.commit()
            print("Datos de prueba (1 cliente y 3 registros de tiempo) creados con éxito.")
        else:
            print("La base de datos ya contiene clientes. Se omite la inserción de datos genéricos.")
            
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error al sembrar datos de prueba en la base de datos: {e}", file=sys.stderr)
    finally:
        if conn:
            conn.close()

    print("=== PROCESO DE INICIALIZACIÓN COMPLETADO ===")

if __name__ == "__main__":
    main()
