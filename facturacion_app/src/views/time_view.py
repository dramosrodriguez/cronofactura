import os
import json
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from src.controllers.client_controller import ClientController
from src.controllers.time_controller import TimeController
from src.controllers.invoice_controller import InvoiceController

# Buscar la ruta absoluta del archivo settings.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")

class TimeView(ctk.CTkFrame):
    """Vista de registro de tiempos de trabajo (manual y cronómetro) y facturación consolidada."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1, uniform="panel")
        self.grid_columnconfigure(1, weight=1, uniform="panel")
        self.grid_rowconfigure(0, weight=1)

        self.clients_map = {}  # Mapeo: "Nombre del Cliente" -> Client Object
        self.all_logs = []  # Caché de registros en memoria para filtrado rápido
        self.preview_data = None  # Almacena el resultado de la pre-facturación

        # Variables de estado del cronómetro
        self.timer_seconds = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_after_id = None
        self.timer_current_log_id = None
        self.manual_current_log_id = None

        # --- PANEL IZQUIERDO: REGISTRO DE HORAS ---
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1) # El listado inferior (Fila 2) se expande verticalmente

        # Tabview para dividir Registro Manual y Cronómetro
        self.tabview = ctk.CTkTabview(self.left_panel)
        self.tabview.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.tabview.add("Registro Manual")
        self.tabview.add("Cronómetro")

        # Configurar columnas de las pestañas
        self.tab_manual = self.tabview.tab("Registro Manual")
        self.tab_manual.grid_columnconfigure(1, weight=1)
        
        self.tab_timer = self.tabview.tab("Cronómetro")
        self.tab_timer.grid_columnconfigure(1, weight=1)

        # ----------------------------------------------------
        # PESTAÑA: REGISTRO MANUAL
        # ----------------------------------------------------
        # Banner de edición de tarea en manual (oculto por defecto)
        self.manual_edit_banner_frame = ctk.CTkFrame(self.tab_manual, fg_color="transparent")
        
        self.lbl_manual_edit_banner = ctk.CTkLabel(
            self.manual_edit_banner_frame, 
            text="✏️ Editando Tarea", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#B7791F", "#D69E2E")
        )
        self.lbl_manual_edit_banner.pack(side="left", padx=5)
        
        self.btn_manual_edit_cancel = ctk.CTkButton(
            self.manual_edit_banner_frame,
            text="✕ Cancelar",
            width=70,
            height=22,
            fg_color="#E53E3E",
            hover_color="#C53030",
            font=ctk.CTkFont(size=10),
            command=self.cancel_manual_edit
        )
        self.btn_manual_edit_cancel.pack(side="left", padx=5)

        # Selección de cliente
        self.lbl_client = ctk.CTkLabel(self.tab_manual, text="Cliente:")
        self.lbl_client.grid(row=1, column=0, sticky="e", padx=(0, 10), pady=6)
        self.cmb_clients = ctk.CTkOptionMenu(self.tab_manual, values=["Cargando clientes..."])
        self.cmb_clients.grid(row=1, column=1, sticky="ew", pady=6)
 
         # Fecha (Con botón selector de calendario)
        self.lbl_date = ctk.CTkLabel(self.tab_manual, text="Fecha (YYYY-MM-DD):")
        self.lbl_date.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=6)
         
        self.date_manual_frame = ctk.CTkFrame(self.tab_manual, fg_color="transparent")
        self.date_manual_frame.grid(row=2, column=1, sticky="ew", pady=6)
        self.date_manual_frame.grid_columnconfigure(0, weight=1)
         
        self.ent_date = ctk.CTkEntry(self.date_manual_frame)
        self.ent_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
         
        self.btn_date_manual = ctk.CTkButton(
            self.date_manual_frame, 
            text="📅", 
            width=32, 
            command=lambda: self.open_date_picker(self.ent_date)
        )
        self.btn_date_manual.grid(row=0, column=1)
 
         # Tiempo Dedicado (Horas y Minutos)
        self.lbl_hours = ctk.CTkLabel(self.tab_manual, text="Tiempo Dedicado:")
        self.lbl_hours.grid(row=3, column=0, sticky="e", padx=(0, 10), pady=6)
        
        self.hours_manual_frame = ctk.CTkFrame(self.tab_manual, fg_color="transparent")
        self.hours_manual_frame.grid(row=3, column=1, sticky="ew", pady=6)
        self.hours_manual_frame.grid_columnconfigure((0, 2), weight=1)
        
        self.ent_hours = ctk.CTkEntry(self.hours_manual_frame, placeholder_text="Ej. 2")
        self.ent_hours.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        self.lbl_h_suffix = ctk.CTkLabel(self.hours_manual_frame, text="h")
        self.lbl_h_suffix.grid(row=0, column=1, padx=(0, 10))
        
        self.ent_minutes = ctk.CTkEntry(self.hours_manual_frame, placeholder_text="Ej. 30")
        self.ent_minutes.grid(row=0, column=2, sticky="ew", padx=(0, 2))
        
        self.lbl_m_suffix = ctk.CTkLabel(self.hours_manual_frame, text="m")
        self.lbl_m_suffix.grid(row=0, column=3)
 
         # Descripción
        self.lbl_desc = ctk.CTkLabel(self.tab_manual, text="Descripción/Detalle:")
        self.lbl_desc.grid(row=4, column=0, sticky="e", padx=(0, 10), pady=6)
        self.ent_desc = ctk.CTkEntry(self.tab_manual, placeholder_text="Describa el trabajo...")
        self.ent_desc.grid(row=4, column=1, sticky="ew", pady=6)
 
         # Observaciones Opcionales
        self.lbl_notes = ctk.CTkLabel(self.tab_manual, text="Observaciones internas (ocultas):")
        self.lbl_notes.grid(row=5, column=0, sticky="e", padx=(0, 10), pady=6)
        self.ent_notes = ctk.CTkEntry(self.tab_manual, placeholder_text="Observaciones de control (opcional)...")
        self.ent_notes.grid(row=5, column=1, sticky="ew", pady=6)
 
         # Botón Guardar Horas Manual
        self.btn_save_log = ctk.CTkButton(
            self.tab_manual, 
            text="Registrar Tarea Manualmente", 
            command=self.save_time_log_manual,
            fg_color="#2B6CB0",
            hover_color="#1A365D",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_save_log.grid(row=6, column=0, columnspan=2, pady=(12, 5), sticky="ew")

        # ----------------------------------------------------
        # PESTAÑA: CRONÓMETRO ASÍNCRONO
        # ----------------------------------------------------
        # Cliente para el cronómetro
        self.lbl_t_client = ctk.CTkLabel(self.tab_timer, text="Cliente:")
        self.lbl_t_client.grid(row=0, column=0, sticky="e", padx=(0, 10), pady=6)
        self.cmb_timer_clients = ctk.CTkOptionMenu(self.tab_timer, values=["Cargando clientes..."])
        self.cmb_timer_clients.grid(row=0, column=1, sticky="ew", pady=6)

        # Descripción de la tarea del cronómetro
        self.lbl_t_desc = ctk.CTkLabel(self.tab_timer, text="Descripción:")
        self.lbl_t_desc.grid(row=1, column=0, sticky="e", padx=(0, 10), pady=6)
        self.ent_timer_desc = ctk.CTkEntry(self.tab_timer, placeholder_text="¿En qué tarea vas a trabajar?")
        self.ent_timer_desc.grid(row=1, column=1, sticky="ew", pady=6)

        # Banner de edición de tarea en cronómetro (oculto por defecto)
        self.timer_edit_banner_frame = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        
        self.lbl_timer_edit_banner = ctk.CTkLabel(
            self.timer_edit_banner_frame, 
            text="", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#B7791F", "#D69E2E")
        )
        self.lbl_timer_edit_banner.pack(side="left", padx=5)
        
        self.btn_timer_edit_cancel = ctk.CTkButton(
            self.timer_edit_banner_frame,
            text="✕ Cancelar",
            width=70,
            height=22,
            fg_color="#E53E3E",
            hover_color="#C53030",
            font=ctk.CTkFont(size=10),
            command=self.cancel_timer_continuation
        )
        self.btn_timer_edit_cancel.pack(side="left", padx=5)

        # Display del Reloj Digital
        self.lbl_timer_clock = ctk.CTkLabel(
            self.tab_timer, 
            text="00:00:00", 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("#2B6CB0", "#90CDF4")
        )
        self.lbl_timer_clock.grid(row=3, column=0, columnspan=2, pady=(15, 10))

        # Botones de control del cronómetro
        self.timer_btns_frame = ctk.CTkFrame(self.tab_timer, fg_color="transparent")
        self.timer_btns_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        self.timer_btns_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_timer_start = ctk.CTkButton(
            self.timer_btns_frame, text="Iniciar", command=self.start_timer, fg_color="#319795", hover_color="#234E52"
        )
        self.btn_timer_start.grid(row=0, column=0, padx=5)

        self.btn_timer_pause = ctk.CTkButton(
            self.timer_btns_frame, text="Pausar", command=self.pause_timer, fg_color="#D69E2E", hover_color="#B7791F", state="disabled"
        )
        self.btn_timer_pause.grid(row=0, column=1, padx=5)

        self.btn_timer_stop = ctk.CTkButton(
            self.timer_btns_frame, text="Parar", command=self.stop_timer, fg_color="#E53E3E", hover_color="#C53030", state="disabled"
        )
        self.btn_timer_stop.grid(row=0, column=2, padx=5)

        # Panel de Resumen/Confirmación de Cronómetro (Oculto inicialmente)
        self.timer_summary_frame = ctk.CTkFrame(self.tab_timer)
        self.timer_summary_frame.grid(row=5, column=0, columnspan=2, pady=(15, 5), padx=5, sticky="ew")
        self.timer_summary_frame.grid_columnconfigure(1, weight=1)
        self.timer_summary_frame.grid_remove()  # Ocultar

        self.lbl_summary_title = ctk.CTkLabel(
            self.timer_summary_frame, text="Confirmar Registro de Tarea", font=ctk.CTkFont(weight="bold")
        )
        self.lbl_summary_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        self.lbl_summary_time = ctk.CTkLabel(self.timer_summary_frame, text="Tiempo acumulado: --", anchor="w")
        self.lbl_summary_time.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=2)

        self.lbl_summary_hours = ctk.CTkLabel(self.timer_summary_frame, text="Horas decimales: --", anchor="w")
        self.lbl_summary_hours.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=2)

        # Fecha de confirmación con selector de fecha
        self.lbl_s_date = ctk.CTkLabel(self.timer_summary_frame, text="Fecha:")
        self.lbl_s_date.grid(row=3, column=0, sticky="e", padx=(10, 5), pady=4)
        
        self.date_summary_frame = ctk.CTkFrame(self.timer_summary_frame, fg_color="transparent")
        self.date_summary_frame.grid(row=3, column=1, sticky="ew", padx=(0, 10), pady=4)
        self.date_summary_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_timer_date = ctk.CTkEntry(self.date_summary_frame)
        self.ent_timer_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_date_summary = ctk.CTkButton(
            self.date_summary_frame, 
            text="📅", 
            width=32, 
            command=lambda: self.open_date_picker(self.ent_timer_date)
        )
        self.btn_date_summary.grid(row=0, column=1)

        # Observaciones del Cronómetro
        self.lbl_s_notes = ctk.CTkLabel(self.timer_summary_frame, text="Observaciones:")
        self.lbl_s_notes.grid(row=4, column=0, sticky="e", padx=(10, 5), pady=4)
        self.ent_timer_notes = ctk.CTkEntry(self.timer_summary_frame, placeholder_text="Observaciones opcionales (ocultas en factura)")
        self.ent_timer_notes.grid(row=4, column=1, sticky="ew", padx=(0, 10), pady=4)

        # Botones de guardado/descarte
        self.timer_action_frame = ctk.CTkFrame(self.timer_summary_frame, fg_color="transparent")
        self.timer_action_frame.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="ew")
        self.timer_action_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_timer_save = ctk.CTkButton(
            self.timer_action_frame, text="Confirmar y Guardar", command=self.save_timer_log, fg_color="#48BB78", hover_color="#38A169"
        )
        self.btn_timer_save.grid(row=0, column=0, padx=5, sticky="ew")

        self.btn_timer_reset = ctk.CTkButton(
            self.timer_action_frame, text="Descartar Tarea", command=lambda: self.reset_timer(confirm=True), fg_color="gray", hover_color="darkgray"
        )
        self.btn_timer_reset.grid(row=0, column=1, padx=5, sticky="ew")


        # --- CABECERA Y FILTROS DEL HISTORIAL (Fila 1) ---
        self.history_header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.history_header_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(15, 5))
        self.history_header_frame.grid_columnconfigure(0, weight=1)

        self.lbl_list_title = ctk.CTkLabel(
            self.history_header_frame, 
            text="Historial de Horas Registradas", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#2B6CB0", "#90CDF4")
        )
        self.lbl_list_title.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Panel de filtros horizontal
        self.filter_controls_frame = ctk.CTkFrame(self.history_header_frame, fg_color="transparent")
        self.filter_controls_frame.grid(row=1, column=0, sticky="ew")
        self.filter_controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Filtro de Cliente
        self.cmb_filter_client = ctk.CTkOptionMenu(
            self.filter_controls_frame, 
            values=["Todos los clientes"],
            command=lambda x: self.filter_logs_list()
        )
        self.cmb_filter_client.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        # Filtro de Mes
        self.cmb_filter_month = ctk.CTkOptionMenu(
            self.filter_controls_frame,
            values=[
                "Todos los meses", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ],
            command=lambda x: self.filter_logs_list()
        )
        self.cmb_filter_month.grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        # Filtro de Año
        self.cmb_filter_year = ctk.CTkOptionMenu(
            self.filter_controls_frame,
            values=["Todos los años", "2025", "2026", "2027", "2028"],
            command=lambda x: self.filter_logs_list()
        )
        self.cmb_filter_year.grid(row=0, column=2, padx=2, pady=2, sticky="ew")


        # --- SCROLL HISTORIAL DE HORAS (Fila 2) ---
        self.logs_scroll = ctk.CTkScrollableFrame(self.left_panel)
        self.logs_scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 15))
        self.logs_scroll.grid_columnconfigure(0, weight=1)


        # --- PANEL DERECHO: FACTURACIÓN CONSOLIDADA ---
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)

        # Formulario de filtros de pre-factura
        self.billing_filter_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.billing_filter_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        self.billing_filter_frame.grid_columnconfigure(1, weight=1)

        self.lbl_billing_title = ctk.CTkLabel(
            self.billing_filter_frame, 
            text="Consolidar y Facturar Horas", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.lbl_billing_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Cliente para Facturación
        self.lbl_bill_client = ctk.CTkLabel(self.billing_filter_frame, text="Cliente:")
        self.lbl_bill_client.grid(row=1, column=0, sticky="e", padx=(0, 10), pady=8)
        self.cmb_bill_clients = ctk.CTkOptionMenu(self.billing_filter_frame, values=["Cargando clientes..."])
        self.cmb_bill_clients.grid(row=1, column=1, sticky="ew", pady=8)

        # Fecha Inicio con selector de fecha
        self.lbl_start_date = ctk.CTkLabel(self.billing_filter_frame, text="Desde:")
        self.lbl_start_date.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=8)
        
        self.date_start_frame = ctk.CTkFrame(self.billing_filter_frame, fg_color="transparent")
        self.date_start_frame.grid(row=2, column=1, sticky="ew", pady=8)
        self.date_start_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_start_date = ctk.CTkEntry(self.date_start_frame)
        self.ent_start_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ent_start_date.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        
        self.btn_date_start = ctk.CTkButton(
            self.date_start_frame, 
            text="📅", 
            width=32, 
            command=lambda: self.open_date_picker(self.ent_start_date)
        )
        self.btn_date_start.grid(row=0, column=1)

        # Fecha Fin con selector de fecha
        self.lbl_end_date = ctk.CTkLabel(self.billing_filter_frame, text="Hasta:")
        self.lbl_end_date.grid(row=3, column=0, sticky="e", padx=(0, 10), pady=8)
        
        self.date_end_frame = ctk.CTkFrame(self.billing_filter_frame, fg_color="transparent")
        self.date_end_frame.grid(row=3, column=1, sticky="ew", pady=8)
        self.date_end_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_end_date = ctk.CTkEntry(self.date_end_frame)
        self.ent_end_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ent_end_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.btn_date_end = ctk.CTkButton(
            self.date_end_frame, 
            text="📅", 
            width=32, 
            command=lambda: self.open_date_picker(self.ent_end_date)
        )
        self.btn_date_end.grid(row=0, column=1)

        # Botón Calcular Pre-factura
        self.btn_preview_invoice = ctk.CTkButton(
            self.billing_filter_frame, 
            text="Calcular Pre-Factura", 
            command=self.calculate_invoice_preview,
            fg_color="#D69E2E",
            hover_color="#B7791F",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_preview_invoice.grid(row=4, column=0, columnspan=2, pady=(10, 5), sticky="ew")

        # Contenedor de Detalle de Pre-factura y Generación Real
        self.preview_container = ctk.CTkScrollableFrame(self.right_panel)
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 15))
        self.preview_container.grid_columnconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(1, weight=1)

        self.lbl_no_preview = ctk.CTkLabel(
            self.preview_container, 
            text="Realice una pre-facturación para ver cálculos e impuestos.", 
            font=ctk.CTkFont(slant="italic")
        )
        self.lbl_no_preview.grid(row=0, column=0, columnspan=2, pady=40)

        # Cargar datos de la base de datos
        self.refresh()

    def refresh(self):
        """Método expuesto para refrescar clientes e históricos."""
        self.load_clients()
        self.refresh_logs_list()

    def load_clients(self):
        """Carga la lista de clientes de la base de datos en los OptionMenu y Filtros."""
        try:
            clients = ClientController.list_clients()
            self.clients_map = {client.name: client for client in clients}
            
            names = list(self.clients_map.keys())
            if not names:
                names = ["No hay clientes registrados"]
            
            self.cmb_clients.configure(values=names)
            self.cmb_clients.set(names[0])

            self.cmb_timer_clients.configure(values=names)
            self.cmb_timer_clients.set(names[0])

            self.cmb_bill_clients.configure(values=names)
            self.cmb_bill_clients.set(names[0])

            # Agregar opción de comodín para el filtro
            filter_names = ["Todos los clientes"] + list(self.clients_map.keys())
            self.cmb_filter_client.configure(values=filter_names)
            self.cmb_filter_client.set("Todos los clientes")
        except Exception as e:
            messagebox.showerror("Error", f"Error al recuperar clientes para formularios: {e}")

    def refresh_logs_list(self):
        """Recupera la lista histórica de tiempos trabajados en caché y dispara el filtrado."""
        try:
            self.all_logs = TimeController.list_logs()
            self.filter_logs_list()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar lista de logs: {e}")

    def filter_logs_list(self):
        """Filtra los logs de horas en caché y los renderiza en el scroll frame."""
        for widget in self.logs_scroll.winfo_children():
            widget.destroy()

        client_filter = self.cmb_filter_client.get()
        month_filter = self.cmb_filter_month.get()
        year_filter = self.cmb_filter_year.get()

        months_map = {
            "Todos los meses": 0, "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
            "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        target_month = months_map.get(month_filter, 0)

        filtered_logs = []
        for log in self.all_logs:
            # 1. Filtro por cliente
            if client_filter != "Todos los clientes" and log["client_name"] != client_filter:
                continue

            # Parsear fecha
            date_parts = log["date"].split("-")
            log_year = date_parts[0]
            log_month = int(date_parts[1])

            # 2. Filtro por año
            if year_filter != "Todos los años" and log_year != year_filter:
                continue

            # 3. Filtro por mes
            if target_month != 0 and log_month != target_month:
                continue

            filtered_logs.append(log)

        if not filtered_logs:
            lbl_empty = ctk.CTkLabel(
                self.logs_scroll, 
                text="No se encontraron horas registradas.", 
                font=ctk.CTkFont(slant="italic")
            )
            lbl_empty.grid(row=0, column=0, pady=20)
            return

        for idx, log in enumerate(filtered_logs):
            bg_color = ("#F7FAFC", "#2D3748") if idx % 2 == 0 else ("#EDF2F7", "#1A202C")
            log_frame = ctk.CTkFrame(self.logs_scroll, fg_color=bg_color, corner_radius=4)
            log_frame.grid(row=idx, column=0, sticky="ew", pady=2, padx=2)
            log_frame.grid_columnconfigure(0, weight=1)
            log_frame.grid_columnconfigure(1, weight=0)
            log_frame.grid_columnconfigure(2, weight=0)

            # Detalle del Log
            billed_status = "Facturado" if log["invoice_id"] is not None else "Pendiente"
            billed_color = "green" if log["invoice_id"] is not None else "#B7791F"
            
            total_minutes = round(log["hours"] * 60)
            h_val = total_minutes // 60
            m_val = total_minutes % 60
            time_str = f"{h_val}h {m_val}m" if h_val > 0 else f"{m_val}m"

            detail_text = f"Fecha: {log['date']} | Cliente: {log['client_name']}\nTiempo: {time_str} ({log['hours']:.2f} h) | {log['description']}"
            if log.get("notes"):
                detail_text += f"\nObservaciones: {log['notes']}"
                
            lbl_details = ctk.CTkLabel(log_frame, text=detail_text, justify="left", font=ctk.CTkFont(size=11))
            lbl_details.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            # Estado
            lbl_status = ctk.CTkLabel(log_frame, text=billed_status, text_color=billed_color, font=ctk.CTkFont(size=10, weight="bold"))
            lbl_status.grid(row=0, column=1, sticky="e", padx=10, pady=5)

            # Botones de Acción (solo para tareas pendientes)
            if log["invoice_id"] is None:
                actions_frame = ctk.CTkFrame(log_frame, fg_color="transparent")
                actions_frame.grid(row=0, column=2, padx=(0, 10), pady=5, sticky="e")
                
                btn_timer = ctk.CTkButton(
                    actions_frame, 
                    text="⏱", 
                    width=28, 
                    height=24,
                    fg_color="#319795",
                    hover_color="#234E52",
                    command=lambda l=log: self.continue_in_timer(l)
                )
                btn_timer.grid(row=0, column=0, padx=2)
                
                btn_edit = ctk.CTkButton(
                    actions_frame,
                    text="✏",
                    width=28,
                    height=24,
                    fg_color="#2B6CB0",
                    hover_color="#1A365D",
                    command=lambda l=log: self.continue_in_manual(l)
                )
                btn_edit.grid(row=0, column=1, padx=2)

    def save_time_log_manual(self):
        """Registra o actualiza el tiempo manualmente en la base de datos."""
        client_name = self.cmb_clients.get()
        date_str = self.ent_date.get().strip()
        hours_str = self.ent_hours.get().strip()
        minutes_str = self.ent_minutes.get().strip()
        desc = self.ent_desc.get().strip()
        notes = self.ent_notes.get().strip()

        # Validaciones
        if client_name == "No hay clientes registrados" or not client_name:
            messagebox.showerror("Error", "Debe registrar un cliente en la sección de Clientes primero.")
            return

        client = self.clients_map.get(client_name)
        if not client:
            messagebox.showerror("Error", "Cliente no seleccionado correctamente.")
            return

        if not desc:
            messagebox.showerror("Error de Validación", "La descripción de la tarea es obligatoria.")
            return

        h = 0
        if hours_str:
            try:
                h = int(hours_str)
                if h < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error de Validación", "Las horas deben ser un número entero mayor o igual a 0.")
                return

        m = 0
        if minutes_str:
            try:
                m = int(minutes_str)
                if m < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error de Validación", "Los minutos deben ser un número entero mayor o igual a 0.")
                return

        if h == 0 and m == 0:
            messagebox.showerror("Error de Validación", "Debe especificar un tiempo de trabajo mayor a 0 (horas y/o minutos).")
            return

        hours_decimal = h + (m / 60.0)

        try:
            if self.manual_current_log_id:
                TimeController.update_log(
                    log_id=self.manual_current_log_id,
                    client_id=client.id,
                    date_str=date_str,
                    hours=hours_decimal,
                    description=desc,
                    notes=notes if notes else None
                )
                messagebox.showinfo("Registro Actualizado", "El registro de tiempo se ha actualizado correctamente.")
                self.cancel_manual_edit()
            else:
                TimeController.create_log(
                    client_id=client.id,
                    date_str=date_str,
                    hours=hours_decimal,
                    description=desc,
                    notes=notes if notes else None
                )
                messagebox.showinfo("Tiempo Registrado", "El registro de tiempo se ha guardado correctamente.")
                self.ent_hours.delete(0, ctk.END)
                self.ent_minutes.delete(0, ctk.END)
                self.ent_desc.delete(0, ctk.END)
                self.ent_notes.delete(0, ctk.END)
            
            self.refresh_logs_list()
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar el registro de tiempo: {e}")

    # ----------------------------------------------------
    # MÉTODOS DEL CRONÓMETRO
    # ----------------------------------------------------
    def start_timer(self):
        """Inicia o reanuda el cronómetro asíncrono."""
        client_name = self.cmb_timer_clients.get()
        desc = self.ent_timer_desc.get().strip()

        if client_name == "No hay clientes registrados" or not client_name:
            messagebox.showerror("Error", "Debe seleccionar un cliente antes de iniciar el cronómetro.")
            return
            
        if not desc:
            messagebox.showerror("Error de Validación", "Debe indicar la descripción de la tarea antes de iniciar.")
            return

        # Si no estaba corriendo, configurar estados
        if not self.timer_running:
            self.timer_running = True
            self.timer_paused = False
            self.run_timer()
        else:
            # Reanudar desde pausa
            self.timer_paused = False

        # Desactivar controles para evitar cambios
        self.cmb_timer_clients.configure(state="disabled")
        self.ent_timer_desc.configure(state="disabled")

        # Configurar botones
        self.btn_timer_start.configure(state="disabled")
        self.btn_timer_pause.configure(state="normal")
        self.btn_timer_stop.configure(state="normal")

        # Ocultar resumen si estaba visible
        self.timer_summary_frame.grid_remove()

    def pause_timer(self):
        """Pausa el conteo del cronómetro."""
        if self.timer_running:
            self.timer_paused = True
            self.btn_timer_start.configure(state="normal", text="Reanudar")
            self.btn_timer_pause.configure(state="disabled")

    def run_timer(self):
        """Método recursivo asíncrono basado en after para contar segundos."""
        if self.timer_running:
            if not self.timer_paused:
                self.timer_seconds += 1
                
                # Formatear visualmente
                h = self.timer_seconds // 3600
                m = (self.timer_seconds % 3600) // 60
                s = self.timer_seconds % 60
                self.lbl_timer_clock.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
                
            self.timer_after_id = self.after(1000, self.run_timer)

    def stop_timer(self):
        """Detiene el cronómetro y abre el panel de confirmación con el resumen de tiempos."""
        if not self.timer_running:
            return

        # Detener loop
        self.timer_running = False
        self.timer_paused = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None

        # Habilitar campos
        self.cmb_timer_clients.configure(state="normal")
        self.ent_timer_desc.configure(state="normal")

        # Configurar botones
        self.btn_timer_start.configure(state="normal", text="Iniciar")
        self.btn_timer_pause.configure(state="disabled")
        self.btn_timer_stop.configure(state="disabled")

        # Mostrar panel de resumen con redondeo a minutos hacia arriba
        total_minutes = (self.timer_seconds + 59) // 60
        h_rounded = total_minutes // 60
        m_rounded = total_minutes % 60
        
        hours_decimal = total_minutes / 60.0
        
        h = self.timer_seconds // 3600
        m = (self.timer_seconds % 3600) // 60
        s = self.timer_seconds % 60
        
        # Actualizar labels
        self.lbl_summary_time.configure(text=f"Tiempo real: {h}h {m}m {s}s -> Redondeado: {h_rounded}h {m_rounded}m")
        self.lbl_summary_hours.configure(text=f"Horas decimales a registrar: {hours_decimal:.4f} h")
        
        # Cargar valores iniciales de confirmación
        self.ent_timer_date.delete(0, ctk.END)
        self.ent_timer_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.ent_timer_notes.delete(0, ctk.END)

        # Mostrar panel
        self.timer_summary_frame.grid()

    def save_timer_log(self):
        """Guarda la tarea del cronómetro confirmada en base de datos."""
        client_name = self.cmb_timer_clients.get()
        desc = self.ent_timer_desc.get().strip()
        date_str = self.ent_timer_date.get().strip()
        notes = self.ent_timer_notes.get().strip()
        
        client = self.clients_map.get(client_name)
        if not client:
            messagebox.showerror("Error", "Error al procesar cliente.")
            return

        # Las horas decimales calculadas redondeando hacia arriba a minutos
        total_minutes = (self.timer_seconds + 59) // 60
        hours_decimal = total_minutes / 60.0
        
        # Validar si el tiempo es cero
        if self.timer_seconds <= 0:
            messagebox.showerror("Error", "El tiempo trabajado debe ser mayor a 0 segundos.")
            return

        try:
            if self.timer_current_log_id:
                TimeController.update_log(
                    log_id=self.timer_current_log_id,
                    client_id=client.id,
                    date_str=date_str,
                    hours=hours_decimal,
                    description=desc,
                    notes=notes if notes else None
                )
                messagebox.showinfo("Registro Actualizado", "La tarea se ha actualizado y guardado exitosamente.")
            else:
                TimeController.create_log(
                    client_id=client.id,
                    date_str=date_str,
                    hours=hours_decimal,
                    description=desc,
                    notes=notes if notes else None
                )
                messagebox.showinfo("Registro Guardado", "La tarea cronometrada se ha guardado exitosamente.")
            
            # Limpiar e inicializar sin confirmación redundante
            self.reset_timer(confirm=False)
            self.refresh_logs_list()
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al guardar la tarea del cronómetro: {e}")

    def reset_timer(self, confirm=False):
        """Descarta el cronómetro y restablece los displays a cero."""
        if confirm:
            q_text = "¿Está seguro de que desea descartar esta tarea?"
            if self.timer_current_log_id:
                q_text = "¿Está seguro de que desea descartar los cambios? La tarea original permanecerá sin modificar."
            ans = messagebox.askyesno("Confirmar Descarte", q_text)
            if not ans:
                return

        self.timer_running = False
        self.timer_paused = False
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
            self.timer_after_id = None
            
        self.timer_seconds = 0
        self.lbl_timer_clock.configure(text="00:00:00")
        self.ent_timer_desc.configure(state="normal")
        self.ent_timer_desc.delete(0, ctk.END)
        self.cmb_timer_clients.configure(state="normal")
        
        self.btn_timer_start.configure(state="normal", text="Iniciar")
        self.btn_timer_pause.configure(state="disabled")
        self.btn_timer_stop.configure(state="disabled")

        # Ocultar panel resumen y banner de edición
        self.timer_summary_frame.grid_remove()
        self.timer_current_log_id = None
        self.timer_edit_banner_frame.grid_remove()

    def open_date_picker(self, entry_widget):
        """Abre la ventana modal del calendario y actualiza el widget de entrada con la fecha elegida."""
        from src.views.date_picker import CTkDatePicker
        val = entry_widget.get().strip()
        
        def handle_selection(date_str):
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, date_str)
            
        CTkDatePicker(self, callback=handle_selection, start_date_str=val)

    def continue_in_timer(self, log):
        """Carga una tarea existente en el cronómetro para continuar sumando tiempo o editarla."""
        if self.timer_running:
            ans = messagebox.askyesno(
                "Cronómetro Activo",
                "Hay una tarea ejecutándose en el cronómetro. ¿Desea pararla y cargar esta tarea?"
            )
            if not ans:
                return
            self.stop_timer()

        # Cambiar a la pestaña Cronómetro
        self.tabview.set("Cronómetro")
        self.timer_current_log_id = log["id"]
        
        # Cargar valores
        if log["client_name"] in self.cmb_timer_clients.cget("values"):
            self.cmb_timer_clients.set(log["client_name"])
        
        self.ent_timer_desc.configure(state="normal")
        self.ent_timer_desc.delete(0, ctk.END)
        self.ent_timer_desc.insert(0, log["description"])
        
        # Cargar tiempo transcurrido (en segundos)
        self.timer_seconds = int(log["hours"] * 3600)
        
        # Formatear y mostrar en el display
        h = self.timer_seconds // 3600
        m = (self.timer_seconds % 3600) // 60
        s = self.timer_seconds % 60
        self.lbl_timer_clock.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
        
        # Mostrar banner
        short_desc = log["description"][:30] + "..." if len(log["description"]) > 30 else log["description"]
        self.lbl_timer_edit_banner.configure(
            text=f"✏️ Continuando: {short_desc}"
        )
        self.timer_edit_banner_frame.grid(row=2, column=0, columnspan=2, pady=(10, 5), sticky="ew")

    def cancel_timer_continuation(self):
        """Cancela la continuación de la tarea en el cronómetro y lo restablece."""
        self.reset_timer(confirm=False)

    def continue_in_manual(self, log):
        """Carga una tarea existente en el formulario manual para su edición."""
        self.tabview.set("Registro Manual")
        
        self.manual_current_log_id = log["id"]
        
        # Cargar valores
        if log["client_name"] in self.cmb_clients.cget("values"):
            self.cmb_clients.set(log["client_name"])
        
        self.ent_date.delete(0, ctk.END)
        self.ent_date.insert(0, log["date"])
        
        # Split decimal hours into hours and minutes
        total_minutes = round(log["hours"] * 60)
        h = total_minutes // 60
        m = total_minutes % 60
        
        self.ent_hours.delete(0, ctk.END)
        self.ent_hours.insert(0, str(h))
        
        self.ent_minutes.delete(0, ctk.END)
        self.ent_minutes.insert(0, str(m))
        
        self.ent_desc.delete(0, ctk.END)
        self.ent_desc.insert(0, log["description"])
        
        self.ent_notes.delete(0, ctk.END)
        self.ent_notes.insert(0, log["notes"] if log.get("notes") else "")
        
        # Mostrar banner
        self.manual_edit_banner_frame.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="ew")
        
        # Cambiar texto y color del botón
        self.btn_save_log.configure(
            text="Actualizar Tarea Manualmente",
            fg_color="#D69E2E",
            hover_color="#B7791F"
        )

    def cancel_manual_edit(self):
        """Cancela la edición manual y limpia los campos."""
        self.manual_current_log_id = None
        self.manual_edit_banner_frame.grid_remove()
        
        # Reset button text and appearance
        self.btn_save_log.configure(
            text="Registrar Tarea Manualmente",
            fg_color="#2B6CB0",
            hover_color="#1A365D"
        )
        
        # Clear fields
        self.ent_hours.delete(0, ctk.END)
        self.ent_minutes.delete(0, ctk.END)
        self.ent_desc.delete(0, ctk.END)
        self.ent_notes.delete(0, ctk.END)
        self.ent_date.delete(0, ctk.END)
        self.ent_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

    # ----------------------------------------------------
    # MÉTODOS DE FACTURACIÓN
    # ----------------------------------------------------
    def calculate_invoice_preview(self):
        """Lanza la vista previa de facturación de horas acumuladas de un cliente."""
        client_name = self.cmb_bill_clients.get()
        start_date = self.ent_start_date.get().strip()
        end_date = self.ent_end_date.get().strip()

        if client_name == "No hay clientes registrados" or not client_name:
            messagebox.showerror("Error", "Debe seleccionar un cliente registrado.")
            return

        client = self.clients_map.get(client_name)
        if not client:
            messagebox.showerror("Error", "Cliente seleccionado no válido.")
            return

        try:
            self.preview_data = InvoiceController.preview_invoice(client.id, start_date, end_date)
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
            return
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al calcular prefactura: {e}")
            return

        # Limpiar contenedor de prefactura
        for widget in self.preview_container.winfo_children():
            widget.destroy()

        if self.preview_data["total_hours"] == 0:
            self.preview_data = None
            lbl_empty = ctk.CTkLabel(
                self.preview_container, 
                text="No se encontraron horas pendientes de facturar\npara este cliente en el rango de fechas seleccionado.",
                font=ctk.CTkFont(slant="italic")
            )
            lbl_empty.grid(row=0, column=0, columnspan=2, pady=30, padx=10)
            return

        self.render_billing_form(client)

    def render_billing_form(self, client):
        """Renderiza los campos detallados e impuestos para pre-facturar."""
        iva_def = 21.0
        irpf_def = 15.0
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    settings = json.load(f)
                impuestos = settings.get("impuestos_defecto", {})
                iva_def = impuestos.get("iva_porcentaje", 21.0)
                irpf_def = impuestos.get("irpf_porcentaje", 15.0)
            except Exception:
                pass

        # Desglose Horas y Subtotal
        lbl_preview_title = ctk.CTkLabel(
            self.preview_container, 
            text="Resumen de Pre-Facturación", 
            font=ctk.CTkFont(weight="bold", size=14)
        )
        lbl_preview_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(5, 10))

        hours_text = f"Total Horas Acumuladas: {self.preview_data['total_hours']:.2f} h"
        self.lbl_p_hours = ctk.CTkLabel(self.preview_container, text=hours_text, anchor="w")
        self.lbl_p_hours.grid(row=1, column=0, columnspan=2, sticky="w", pady=2)

        rate_text = f"Tarifa Aplicada del Cliente: {self.preview_data['client_rate']:.2f} €/h"
        lbl_p_rate = ctk.CTkLabel(self.preview_container, text=rate_text, anchor="w")
        lbl_p_rate.grid(row=2, column=0, columnspan=2, sticky="w", pady=2)

        subtotal_text = f"Subtotal Calculado: {self.preview_data['subtotal']:.2f} €"
        self.lbl_p_sub = ctk.CTkLabel(self.preview_container, text=subtotal_text, anchor="w", font=ctk.CTkFont(weight="bold"))
        self.lbl_p_sub.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 10))

        # Tareas Incluidas en la Pre-Facturación
        lbl_tasks_title = ctk.CTkLabel(
            self.preview_container, 
            text="Tareas Incluidas:", 
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#2B6CB0", "#90CDF4")
        )
        lbl_tasks_title.grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 2))

        # Checkbox maestro para seleccionar todas las tareas
        self.chk_select_all = ctk.CTkCheckBox(
            self.preview_container, 
            text="Seleccionar todas las tareas", 
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_select_all
        )
        self.chk_select_all.grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=(2, 5))
        self.chk_select_all.select() # Por defecto seleccionados

        self.tasks_list_frame = ctk.CTkFrame(self.preview_container)
        self.tasks_list_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5, padx=2)
        self.tasks_list_frame.grid_columnconfigure(0, weight=0) # Checkbox
        self.tasks_list_frame.grid_columnconfigure(1, weight=1) # Descripción
        self.tasks_list_frame.grid_columnconfigure(2, weight=0) # Horas

        self.task_check_vars = {}

        for idx, log in enumerate(self.preview_data["logs"]):
            bg_color = ("#F7FAFC", "#2D3748") if idx % 2 == 0 else ("#EDF2F7", "#1A202C")
            row_frame = ctk.CTkFrame(self.tasks_list_frame, fg_color=bg_color, corner_radius=4)
            row_frame.grid(row=idx, column=0, sticky="ew", pady=1, padx=2)
            row_frame.grid_columnconfigure(0, weight=0) # checkbox
            row_frame.grid_columnconfigure(1, weight=1) # description
            row_frame.grid_columnconfigure(2, weight=0) # hours

            # Checkbox individual
            var = ctk.BooleanVar(value=True)
            self.task_check_vars[log.id] = var
            chk = ctk.CTkCheckBox(
                row_frame, 
                text="", 
                variable=var, 
                width=24, 
                command=self.update_totals_from_selection
            )
            chk.grid(row=0, column=0, padx=(8, 2), pady=4, sticky="w")

            # Información de la tarea
            desc_text = f"{log.date} | {log.description}"
            if log.notes:
                desc_text += f"\nObservación: {log.notes}"

            lbl_t_desc = ctk.CTkLabel(row_frame, text=desc_text, justify="left", font=ctk.CTkFont(size=11))
            lbl_t_desc.grid(row=0, column=1, sticky="w", padx=4, pady=4)

            # Horas de la tarea
            lbl_t_hours = ctk.CTkLabel(row_frame, text=f"{log.hours:.2f} h", font=ctk.CTkFont(size=11, weight="bold"))
            lbl_t_hours.grid(row=0, column=2, sticky="e", padx=8, pady=4)

        # Configuración Formulario Factura Real
        lbl_bill_form_title = ctk.CTkLabel(
            self.preview_container, 
            text="Datos de Emisión de Factura", 
            font=ctk.CTkFont(weight="bold", size=13),
            text_color=("#2B6CB0", "#90CDF4")
        )
        lbl_bill_form_title.grid(row=7, column=0, columnspan=2, sticky="w", pady=(15, 5))

        # Número Factura
        lbl_num = ctk.CTkLabel(self.preview_container, text="Nº Factura único:")
        lbl_num.grid(row=8, column=0, sticky="e", padx=(0, 5), pady=5)
        self.ent_bill_number = ctk.CTkEntry(self.preview_container, placeholder_text="Ej. F2026-001")
        self.ent_bill_number.grid(row=8, column=1, sticky="ew", pady=5)

        # Tipo de Cobro
        lbl_type = ctk.CTkLabel(self.preview_container, text="Tipo de Cobro:")
        lbl_type.grid(row=9, column=0, sticky="e", padx=(0, 5), pady=5)
        
        self.seg_billing_type = ctk.CTkSegmentedButton(
            self.preview_container,
            values=["Por Horas", "Por Proyecto"],
            command=self.toggle_billing_type
        )
        self.seg_billing_type.grid(row=9, column=1, sticky="ew", pady=5)
        self.seg_billing_type.set("Por Horas")

        # Contenedor de campos adicionales de Proyecto (oculto por defecto)
        self.project_fields_frame = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.project_fields_frame.grid(row=10, column=0, columnspan=2, sticky="ew", pady=2)
        self.project_fields_frame.grid_columnconfigure(1, weight=1)

        lbl_proj_concept = ctk.CTkLabel(self.project_fields_frame, text="Concepto Proyecto:")
        lbl_proj_concept.grid(row=0, column=0, sticky="e", padx=(10, 5), pady=5)
        self.ent_proj_concept = ctk.CTkEntry(self.project_fields_frame, placeholder_text="Ej. Desarrollo de Web Corporativa")
        self.ent_proj_concept.grid(row=0, column=1, sticky="ew", pady=5)
        self.ent_proj_concept.insert(0, "Servicios profesionales según proyecto")

        lbl_proj_amount = ctk.CTkLabel(self.project_fields_frame, text="Importe Proyecto (€):")
        lbl_proj_amount.grid(row=1, column=0, sticky="e", padx=(10, 5), pady=5)
        self.ent_proj_amount = ctk.CTkEntry(self.project_fields_frame)
        self.ent_proj_amount.grid(row=1, column=1, sticky="ew", pady=5)
        self.ent_proj_amount.insert(0, f"{self.preview_data['subtotal']:.2f}")

        # Ocultar campos de proyecto inicialmente
        self.project_fields_frame.grid_remove()

        # IVA
        lbl_iva = ctk.CTkLabel(self.preview_container, text="IVA (%):")
        lbl_iva.grid(row=11, column=0, sticky="e", padx=(0, 5), pady=5)
        self.ent_bill_iva = ctk.CTkEntry(self.preview_container)
        self.ent_bill_iva.grid(row=11, column=1, sticky="ew", pady=5)
        self.ent_bill_iva.insert(0, str(iva_def))

        # IRPF
        lbl_irpf = ctk.CTkLabel(self.preview_container, text="IRPF (%):")
        lbl_irpf.grid(row=12, column=0, sticky="e", padx=(0, 5), pady=5)
        self.ent_bill_irpf = ctk.CTkEntry(self.preview_container)
        self.ent_bill_irpf.grid(row=12, column=1, sticky="ew", pady=5)
        self.ent_bill_irpf.insert(0, str(irpf_def))

        # Fecha de Emisión con selector
        lbl_iss_date = ctk.CTkLabel(self.preview_container, text="Fecha Emisión:")
        lbl_iss_date.grid(row=13, column=0, sticky="e", padx=(0, 5), pady=5)
        
        self.date_iss_frame = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.date_iss_frame.grid(row=13, column=1, sticky="ew", pady=5)
        self.date_iss_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_bill_iss_date = ctk.CTkEntry(self.date_iss_frame)
        self.ent_bill_iss_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ent_bill_iss_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        self.btn_date_iss = ctk.CTkButton(
            self.date_iss_frame, 
            text="📅", 
            width=32, 
            command=lambda: self.open_date_picker(self.ent_bill_iss_date)
        )
        self.btn_date_iss.grid(row=0, column=1)

        # Fecha de Vencimiento con selector
        lbl_due_date = ctk.CTkLabel(self.preview_container, text="Fecha Vencimiento:")
        lbl_due_date.grid(row=14, column=0, sticky="e", padx=(0, 5), pady=5)
        
        self.date_due_frame = ctk.CTkFrame(self.preview_container, fg_color="transparent")
        self.date_due_frame.grid(row=14, column=1, sticky="ew", pady=5)
        self.date_due_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_bill_due_date = ctk.CTkEntry(self.date_due_frame)
        self.ent_bill_due_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.ent_bill_due_date.insert(0, (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"))
        
        self.btn_date_due = ctk.CTkButton(
            self.date_due_frame, 
            text="📅", 
            width=32, 
            command=lambda: self.open_date_picker(self.ent_bill_due_date)
        )
        self.btn_date_due.grid(row=0, column=1)
        # Botón Final
        # Verificar si el cliente está completo (nombre, NIF real, email, dirección, tarifa > 0)
        is_client_complete = bool(
            client.name and client.name.strip() and
            client.nif and client.nif.strip() and not client.nif.startswith("PENDIENTE-") and
            client.email and client.email.strip() and
            client.address and client.address.strip() and
            client.hourly_rate > 0
        )

        # Botón Final
        if not is_client_complete:
            self.btn_submit_invoice = ctk.CTkButton(
                self.preview_container, 
                text="Emisión Deshabilitada (Datos de Cliente Incompletos)", 
                state="disabled",
                fg_color="gray",
                hover_color="gray",
                font=ctk.CTkFont(weight="bold")
            )
        else:
            self.btn_submit_invoice = ctk.CTkButton(
                self.preview_container, 
                text="Emitir Factura y Crear PDF", 
                command=lambda: self.submit_invoice(client.id),
                fg_color="#48BB78",
                hover_color="#38A169",
                font=ctk.CTkFont(weight="bold")
            )
        self.btn_submit_invoice.grid(row=15, column=0, columnspan=2, pady=(15, 10), sticky="ew")

        # Mostrar aviso si el cliente no está completo
        if not is_client_complete:
            self.lbl_billing_warning = ctk.CTkLabel(
                self.preview_container,
                text="⚠️ Complete el NIF, Email, Dirección y Tarifa del cliente para emitir la factura final.",
                text_color=("#E53E3E", "#FC8181"),
                font=ctk.CTkFont(size=11, weight="bold")
            )
            self.lbl_billing_warning.grid(row=16, column=0, columnspan=2, pady=(0, 10), sticky="ew", padx=10)

    def submit_invoice(self, client_id: int):
        """Lanza la facturación real y generación de archivos."""
        client = ClientController.get_client(client_id)
        is_client_complete = bool(
            client.name and client.name.strip() and
            client.nif and client.nif.strip() and not client.nif.startswith("PENDIENTE-") and
            client.email and client.email.strip() and
            client.address and client.address.strip() and
            client.hourly_rate > 0
        )
        if not is_client_complete:
            messagebox.showerror("Error de Facturación", "No se puede emitir la factura final porque el cliente tiene datos incompletos.")
            return

        invoice_number = self.ent_bill_number.get().strip()
        iva_str = self.ent_bill_iva.get().strip()
        irpf_str = self.ent_bill_irpf.get().strip()
        issue_date = self.ent_bill_iss_date.get().strip()
        due_date = self.ent_bill_due_date.get().strip()

        start_date = self.ent_start_date.get().strip()
        end_date = self.ent_end_date.get().strip()

        if not invoice_number or not iva_str or not irpf_str or not issue_date or not due_date:
            messagebox.showerror("Error de Validación", "Todos los campos de la emisión de factura son obligatorios.")
            return

        try:
            vat_rate = float(iva_str)
            irpf_rate = float(irpf_str)
            if vat_rate < 0 or irpf_rate < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de Validación", "Las tasas de impuestos deben ser valores numéricos positivos.")
            return

        # Obtener los IDs de las tareas seleccionadas
        selected_log_ids = [log_id for log_id, var in self.task_check_vars.items() if var.get()]
        if not selected_log_ids:
            messagebox.showerror("Error de Validación", "Debe seleccionar al menos una tarea para facturar.")
            return

        # Obtener tipo de cobro y datos de proyecto si corresponde
        billing_type_selected = self.seg_billing_type.get()
        billing_type = "proyecto" if billing_type_selected == "Por Proyecto" else "horas"
        project_concept = None
        custom_subtotal = None

        if billing_type == "proyecto":
            project_concept = self.ent_proj_concept.get().strip()
            if not project_concept:
                messagebox.showerror("Error de Validación", "El concepto del proyecto es obligatorio para cobros por proyecto.")
                return
            
            amount_str = self.ent_proj_amount.get().strip()
            if not amount_str:
                messagebox.showerror("Error de Validación", "El importe del proyecto es obligatorio.")
                return
            try:
                custom_subtotal = float(amount_str)
                if custom_subtotal < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error de Validación", "El importe del proyecto debe ser un valor numérico positivo.")
                return

        try:
            invoice = InvoiceController.create_invoice(
                invoice_number=invoice_number,
                client_id=client_id,
                start_date_str=start_date,
                end_date_str=end_date,
                issue_date_str=issue_date,
                due_date_str=due_date,
                vat_rate=vat_rate,
                irpf_rate=irpf_rate,
                billing_type=billing_type,
                project_concept=project_concept,
                custom_subtotal=custom_subtotal,
                selected_log_ids=selected_log_ids
            )
            
            messagebox.showinfo(
                "Factura Emitida", 
                f"La Factura {invoice.invoice_number} fue creada y consolidada correctamente.\n"
                f"Archivo PDF guardado en:\n{invoice.pdf_path}"
            )
            
            self.preview_data = None
            for widget in self.preview_container.winfo_children():
                widget.destroy()
            
            lbl_empty = ctk.CTkLabel(
                self.preview_container, 
                text="Realice una pre-facturación para ver cálculos e impuestos.", 
                font=ctk.CTkFont(slant="italic")
            )
            lbl_empty.grid(row=0, column=0, columnspan=2, pady=40)

            self.refresh_logs_list()
            
        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error de Facturación", f"Ocurrió un error al procesar la factura: {e}")

    def toggle_billing_type(self, value):
        """Muestra u oculta los campos de proyecto según la selección."""
        if value == "Por Proyecto":
            self.project_fields_frame.grid()
        else:
            self.project_fields_frame.grid_remove()

    def toggle_select_all(self):
        """Marca o desmarca todas las tareas según el estado del checkbox maestro."""
        state = self.chk_select_all.get()
        for var in self.task_check_vars.values():
            var.set(state)
        self.update_totals_from_selection()

    def update_totals_from_selection(self):
        """Actualiza en tiempo real los totales del resumen al marcar/desmarcar tareas."""
        selected_hours = 0.0
        selected_count = 0
        for log in self.preview_data["logs"]:
            if self.task_check_vars[log.id].get():
                selected_hours += log.hours
                selected_count += 1

        client_rate = self.preview_data["client_rate"]
        selected_subtotal = selected_hours * client_rate

        # Actualizar etiquetas del resumen
        self.lbl_p_hours.configure(text=f"Total Horas Acumuladas: {selected_hours:.2f} h")
        self.lbl_p_sub.configure(text=f"Subtotal Calculado: {selected_subtotal:.2f} €")

        # Actualizar importe del proyecto si la vista de proyecto está activa y el input existe
        if hasattr(self, 'ent_proj_amount') and self.ent_proj_amount.winfo_exists():
            self.ent_proj_amount.delete(0, ctk.END)
            self.ent_proj_amount.insert(0, f"{selected_subtotal:.2f}")

        # Mantener el checkbox maestro alinear
        all_selected = (selected_count == len(self.preview_data["logs"]))
        # Desactivar temporalmente el comando del master checkbox al cambiar su estado programáticamente
        self.chk_select_all.configure(command=None)
        if all_selected:
            self.chk_select_all.select()
        else:
            self.chk_select_all.deselect()
        self.chk_select_all.configure(command=self.toggle_select_all)
