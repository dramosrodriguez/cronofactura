import sys
import os

# Asegurar que el directorio raíz del proyecto está en el PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from src.database.db_manager import DatabaseManager
from src.views.main_window import AplicacionFacturacion

def main():
    """Punto de entrada principal para inicializar la base de datos y arrancar la GUI."""
    
    # 1. Configurar la apariencia inicial
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # 2. Inicializar base de datos y aplicar migraciones
    try:
        DatabaseManager.init_db()
    except Exception as e:
        print(f"Error crítico al inicializar la base de datos: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Limpiar archivos temporales de actualizaciones pasadas si existen
    try:
        from src.utils.update_manager import UpdateManager
        UpdateManager.cleanup_temp_files()
    except Exception as e:
        print(f"Advertencia al limpiar archivos temporales de actualización: {e}", file=sys.stderr)

    # 4. Arrancar la interfaz gráfica principal
    try:
        app = AplicacionFacturacion()
        app.mainloop()
    except Exception as e:
        print(f"Error al arrancar la interfaz gráfica de usuario: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
