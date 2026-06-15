import customtkinter as ctk
from src.views.dashboard_view import DashboardView
from src.views.clients_view import ClientsView
from src.views.time_view import TimeView
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

        # Configurar grid layout (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar (ancho fijo)
        self.grid_columnconfigure(1, weight=1)  # Contenedor dinámico (flexible)

        self.current_view_name = None

        # --- BARRA LATERAL (SIDEBAR) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)  # Espacio flexible antes de la config de apariencia

        # Logo / Título de la App
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="AutónomoOS", 
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

        # Selector de Tema / Apariencia (Al final del Sidebar)
        self.lbl_appearance = ctk.CTkLabel(self.sidebar_frame, text="Apariencia:", font=ctk.CTkFont(size=11))
        self.lbl_appearance.grid(row=6, column=0, padx=20, pady=(10, 2), sticky="w")
        
        self.cmb_appearance = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            command=self.change_appearance_mode,
            height=28
        )
        self.cmb_appearance.grid(row=7, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Botón 4: Configuración (Bajo el selector de tema por estética)
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
        self.btn_settings.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Lista de botones para facilitar resaltado dinámico
        self.nav_buttons = {
            "dashboard": self.btn_dashboard,
            "clients": self.btn_clients,
            "time": self.btn_time,
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
            "settings": SettingsView(self.main_container)
        }

        # Mostrar la primera vista por defecto (Dashboard)
        self.select_view("dashboard")

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
