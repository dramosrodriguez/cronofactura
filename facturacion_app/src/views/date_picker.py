import calendar
from datetime import datetime
import customtkinter as ctk

class CTkDatePicker(ctk.CTkToplevel):
    """Diálogo modal interactivo para seleccionar fechas mediante un calendario visual."""

    def __init__(self, parent, callback, start_date_str=None):
        super().__init__(parent)
        
        self.title("Seleccionar Fecha")
        self.geometry("290x340")
        self.resizable(False, False)
        
        # Centrar el popup con respecto al parent si es posible
        if parent:
            self.transient(parent)
            # Intentar obtener posiciones
            parent.update_idletasks()
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 145
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 170
            self.geometry(f"+{x}+{y}")
            
        self.grab_set()  # Bloquear la ventana principal hasta cerrar este diálogo
        self.focus_set()

        self.callback = callback

        # Parsear la fecha de inicio
        try:
            if start_date_str:
                self.current_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            else:
                self.current_date = datetime.now().date()
        except ValueError:
            self.current_date = datetime.now().date()

        self.selected_year = self.current_date.year
        self.selected_month = self.current_date.month

        # Configurar grilla del contenedor principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Nombres de meses en español
        self.month_names = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        # --- CABECERA: Mes, Año y Navegación ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.header_frame.grid_columnconfigure(1, weight=1)

        self.btn_prev = ctk.CTkButton(
            self.header_frame, 
            text="<", 
            width=30, 
            height=30,
            command=self.prev_month,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_prev.grid(row=0, column=0, padx=2)

        self.lbl_month_year = ctk.CTkLabel(
            self.header_frame, 
            text="", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#1A365D", "#90CDF4")
        )
        self.lbl_month_year.grid(row=0, column=1)

        self.btn_next = ctk.CTkButton(
            self.header_frame, 
            text=">", 
            width=30, 
            height=30,
            command=self.next_month,
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_next.grid(row=0, column=2, padx=2)

        # --- DÍAS DE LA SEMANA ---
        self.weeks_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.weeks_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.weeks_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        
        days_headers = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for col_idx, day_name in enumerate(days_headers):
            lbl = ctk.CTkLabel(
                self.weeks_frame, 
                text=day_name, 
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="gray"
            )
            lbl.grid(row=0, column=col_idx, sticky="ew")

        # --- GRILLA DEL CALENDARIO ---
        self.days_frame = ctk.CTkFrame(self)
        self.days_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.days_frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.days_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.draw_calendar()

    def draw_calendar(self):
        """Dibuja los botones de días correspondientes al mes y año seleccionados."""
        # Limpiar botones anteriores
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        # Actualizar título de cabecera
        month_name = self.month_names[self.selected_month - 1]
        self.lbl_month_year.configure(text=f"{month_name} {self.selected_year}")

        # Obtener matriz de días del mes
        # el primer día de la semana es Lunes (0)
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.selected_year, self.selected_month)

        today = datetime.now().date()

        for row_idx, week in enumerate(month_days):
            for col_idx, day in enumerate(week):
                if day == 0:
                    # Relleno vacío para días fuera de mes
                    lbl_empty = ctk.CTkLabel(self.days_frame, text="", fg_color="transparent")
                    lbl_empty.grid(row=row_idx, column=col_idx, sticky="nsew")
                else:
                    # Determinar color especial si es el día actual seleccionado o hoy
                    is_today = (
                        self.selected_year == today.year and
                        self.selected_month == today.month and
                        day == today.day
                    )
                    is_current = (
                        self.selected_year == self.current_date.year and
                        self.selected_month == self.current_date.month and
                        day == self.current_date.day
                    )

                    if is_current:
                        fg_color = "#2B6CB0"
                        hover_color = "#1A365D"
                        text_color = "white"
                    elif is_today:
                        fg_color = "#319795"
                        hover_color = "#234E52"
                        text_color = "white"
                    else:
                        fg_color = "transparent"
                        hover_color = ("#EDF2F7", "#2D3748")
                        text_color = ("black", "white")

                    btn_day = ctk.CTkButton(
                        self.days_frame,
                        text=str(day),
                        fg_color=fg_color,
                        hover_color=hover_color,
                        text_color=text_color,
                        width=25,
                        height=25,
                        corner_radius=4,
                        font=ctk.CTkFont(size=11),
                        command=lambda d=day: self.select_day(d)
                    )
                    btn_day.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky="nsew")

    def select_day(self, day):
        """Invoca al callback con la fecha formateada y destruye el diálogo."""
        date_str = f"{self.selected_year:04d}-{self.selected_month:02d}-{day:02d}"
        self.callback(date_str)
        self.destroy()

    def prev_month(self):
        """Navega al mes anterior."""
        self.selected_month -= 1
        if self.selected_month == 0:
            self.selected_month = 12
            self.selected_year -= 1
        self.draw_calendar()

    def next_month(self):
        """Navega al siguiente mes."""
        self.selected_month += 1
        if self.selected_month == 13:
            self.selected_month = 1
            self.selected_year += 1
        self.draw_calendar()
