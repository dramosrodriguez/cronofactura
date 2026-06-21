import customtkinter as ctk
from src.views.dashboard_view import DashboardView
from src.views.clients_view import ClientsView
from src.views.time_view import TimeView
from src.views.history_view import HistoryView
from src.views.settings_view import SettingsView

class AplicacionFacturacion(ctk.CTk):
    """Clase principal de la ventana de la aplicación de Facturación y Tiempos."""

    def __init__(self):
        super().__init__()
        from src import __version__
        self.title(f"Sistema Local de Facturación y Gestión de Tiempos - v{__version__}")
        self.geometry("1150x700")
        self.minimum_width = 900
        self.minimum_height = 600
        self.minsize(self.minimum_width, self.minimum_height)

        # Configurar icono de la aplicación (ventana y barra de tareas)
        try:
            import sys
            import os
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 1. Configurar AppUserModelID en Windows para que se muestre el icono personalizado en la barra de tareas
            if sys.platform.startswith("win"):
                import ctypes
                myappid = 'dramosrodriguez.cronofactura.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                
                # Asignar icono .ico
                ico_path = os.path.join(current_dir, "..", "assets", "icon.ico")
                if os.path.exists(ico_path):
                    self.iconbitmap(ico_path)
            else:
                # Usar .png para otros sistemas operativos
                png_path = os.path.join(current_dir, "..", "assets", "icon.png")
                if os.path.exists(png_path):
                    from PIL import Image, ImageTk
                    img = Image.open(png_path)
                    photo = ImageTk.PhotoImage(img)
                    self.iconphoto(False, photo)
        except Exception as e:
            print(f"Advertencia al configurar el icono de la ventana: {e}", file=sys.stderr)

        # Configurar grid layout (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar (ancho fijo)
        self.grid_columnconfigure(1, weight=1)  # Contenedor dinámico (flexible)

        self.current_view_name = None

        # --- BARRA LATERAL (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)  # Espacio flexible antes de la config de apariencia

        # Logo / Título de la App
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="CronoFactura", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1A365D", "#90CDF4")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Gestión de Facturación", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 25))

        # Botón 1: Dashboard
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame, 
            text="Dashboard", 
            anchor="w",
            height=40,
            command=lambda: self.select_view("dashboard"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_dashboard.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        # Botón 2: Clientes
        self.btn_clients = ctk.CTkButton(
            self.sidebar_frame, 
            text="Clientes", 
            anchor="w",
            height=40,
            command=lambda: self.select_view("clients"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_clients.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        # Botón 3: Horas y Facturas
        self.btn_time = ctk.CTkButton(
            self.sidebar_frame, 
            text="Registro y Facturación", 
            anchor="w",
            height=40,
            command=lambda: self.select_view("time"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_time.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        # Botón 4: Historial y Gestión
        self.btn_history = ctk.CTkButton(
            self.sidebar_frame, 
            text="Historial y Gestión", 
            anchor="w",
            height=40,
            command=lambda: self.select_view("history"),
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.btn_history.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        # Selector de Tema / Apariencia (Al final del Sidebar)
        self.lbl_appearance = ctk.CTkLabel(self.sidebar_frame, text="Apariencia:", font=ctk.CTkFont(size=11))
        self.lbl_appearance.grid(row=7, column=0, padx=20, pady=(10, 2), sticky="w")
        
        self.cmb_appearance = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode,
            height=28
        )
        self.cmb_appearance.grid(row=8, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Leer apariencia guardada para el OptionMenu
        saved_appearance = "System"
        try:
            import json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(current_dir))
            settings_path = os.path.join(base_dir, "config", "settings.json")
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    saved_appearance = config.get("apariencia", "System")
        except Exception:
            pass
        self.cmb_appearance.set(saved_appearance)

        # Botón 5: Configuración (Bajo el selector de tema por estética)
        self.btn_settings = ctk.CTkButton(
            self.sidebar_frame, 
            text="Configuración", 
            anchor="w",
            height=40,
            command=lambda: self.select_view("settings"),
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=("black", "white"),
            border_width=1,
            border_color=("#CBD5E0", "#4A5568")
        )
        self.btn_settings.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Lista de botones para facilitar resaltado dinámico
        self.nav_buttons = {
            "dashboard": self.btn_dashboard,
            "clients": self.btn_clients,
            "time": self.btn_time,
            "history": self.btn_history,
            "settings": self.btn_settings
        }

        # --- CONTENEDOR DERECHO (PRINCIPAL) ---
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Instanciar las vistas de manera perezosa o inicializarlas
        self.views = {
            "dashboard": DashboardView(self.main_container),
            "clients": ClientsView(self.main_container),
            "time": TimeView(self.main_container),
            "history": HistoryView(self.main_container),
            "settings": SettingsView(self.main_container)
        }

        # Mostrar la primera vista por defecto (Dashboard)
        self.select_view("dashboard")

        # Comprobar actualizaciones en segundo plano tras 1 segundo
        self.after(1000, self.verificar_actualizaciones)

    def select_view(self, view_name: str):
        """Alterna el frame visible en el contenedor derecho y refresca su estado."""
        if self.current_view_name == view_name:
            return

        # 1. Ocultar la vista previa activa
        if self.current_view_name:
            self.views[self.current_view_name].grid_forget()

        # 2. Resaltar botón en el sidebar
        for name, button in self.nav_buttons.items():
            if name == view_name:
                # Estilo activo
                if name == "settings":
                    button.configure(fg_color=("#CBD5E0", "#4A5568"))
                else:
                    button.configure(fg_color=("#2B6CB0", "#1D4ED8"), text_color="white")
            else:
                # Estilo inactivo
                if name == "settings":
                    button.configure(fg_color="transparent", text_color=("black", "white"))
                else:
                    button.configure(fg_color="transparent", text_color=("black", "white"))

        # 3. Invocar actualización de datos en la vista antes de mostrarla
        view = self.views[view_name]
        if hasattr(view, "refresh"):
            view.refresh()

        # 4. Mostrar nueva vista
        view.grid(row=0, column=0, sticky="nsew")
        self.current_view_name = view_name

    def change_appearance_mode(self, new_mode: str):
        """Cambia el modo de color de la interfaz (Oscuro/Claro/Sistema)."""
        ctk.set_appearance_mode(new_mode)
        
        # Guardar en settings.json
        try:
            import json
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(os.path.dirname(current_dir))
            settings_path = os.path.join(base_dir, "config", "settings.json")
            
            config_data = {}
            if os.path.exists(settings_path):
                with open(settings_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            
            config_data["apariencia"] = new_mode
            
            os.makedirs(os.path.dirname(settings_path), exist_ok=True)
            tmp_path = settings_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(settings_path):
                os.replace(tmp_path, settings_path)
            else:
                os.rename(tmp_path, settings_path)
        except Exception as e:
            import sys
            print(f"Error al guardar la apariencia en la configuración: {e}", file=sys.stderr)

    def verificar_actualizaciones(self):
        """Inicia la comprobación de actualizaciones en segundo plano."""
        from src.utils.update_manager import UpdateManager
        from src import __version__

        def callback(result):
            # Esta callback se ejecuta en el hilo secundario
            if result and result.get("update_available"):
                # Agendar la visualización del diálogo en el hilo principal de la UI
                self.after(0, lambda: self.mostrar_dialogo_actualizacion(result))

        UpdateManager.check_for_updates_async(__version__, callback)

    def mostrar_dialogo_actualizacion(self, version_info):
        """Muestra el diálogo para notificar la nueva versión disponible."""
        from src.views.update_dialogs import UpdateDialog
        dialog = UpdateDialog(self, version_info, lambda: self.iniciar_descarga_actualizacion(version_info["zipball_url"]))

    def iniciar_descarga_actualizacion(self, zipball_url):
        """Muestra la ventana de progreso e inicia la descarga en segundo plano."""
        import threading
        from tkinter import messagebox
        from src.views.update_dialogs import DownloadProgressDialog
        from src.utils.update_manager import UpdateManager

        progress_dialog = DownloadProgressDialog(self)

        def run_download():
            def progress_cb(percent, bytes_downloaded):
                # Actualizar progreso en el hilo principal
                self.after(0, lambda: progress_dialog.update_progress(percent, bytes_downloaded))

            success = UpdateManager.download_and_extract_update(zipball_url, progress_cb)
            # Procesar finalización de la descarga en el hilo principal
            self.after(0, lambda: finalizar_descarga(success))

        def finalizar_descarga(success):
            progress_dialog.destroy()
            if success:
                try:
                    UpdateManager.launch_external_updater()
                    self.destroy()  # Cerrar la aplicación principal para liberar archivos
                except Exception as e:
                    messagebox.showerror("Error de Actualización", f"No se pudo iniciar el instalador externo: {e}")
            else:
                messagebox.showerror("Error de Descarga", "No se pudo descargar o descomprimir la actualización desde GitHub.")

        download_thread = threading.Thread(target=run_download, daemon=True)
        download_thread.start()
