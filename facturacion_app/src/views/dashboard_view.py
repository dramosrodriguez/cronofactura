import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from src.models.invoice import Invoice
from src.models.client import Client
from src.utils.excel_exporter import ExcelExporter

class DashboardView(ctk.CTkFrame):
    """Vista de Dashboard con resúmenes, KPIs y herramientas de exportación."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # El área inferior es flexible

        # Título
        self.title_label = ctk.CTkLabel(
            self, 
            text="Panel de Control (Dashboard)", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1A365D", "#90CDF4")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        # --- PANEL SUPERIOR: TARJETAS KPI ---
        self.kpis_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpis_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        # 4 columnas para 4 tarjetas
        self.kpis_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Tarjeta 1: Total Facturado (Bruto)
        self.card_total = self.create_kpi_card(self.kpis_frame, "Total Facturado (Neto + IVA)", "0.00 €", "#2B6CB0", 0)

        # Tarjeta 2: Subtotal Facturado (Sin Impuestos)
        self.card_subtotal = self.create_kpi_card(self.kpis_frame, "Subtotal Trabajos", "0.00 €", "#319795", 1)

        # Tarjeta 3: Número de Facturas
        self.card_invoices = self.create_kpi_card(self.kpis_frame, "Facturas Emitidas", "0", "#D69E2E", 2)

        # Tarjeta 4: Total Clientes
        self.card_clients = self.create_kpi_card(self.kpis_frame, "Clientes Activos", "0", "#4A5568", 3)


        # --- PANEL INFERIOR: HISTORIAL Y EXPORTACIONES ---
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.bottom_frame.grid_columnconfigure(0, weight=3) # Historial ocupa más
        self.bottom_frame.grid_columnconfigure(1, weight=2) # Exportación ocupa menos
        self.bottom_frame.grid_rowconfigure(0, weight=1)

        # Historial de Facturas (Izquierda)
        self.history_panel = ctk.CTkFrame(self.bottom_frame)
        self.history_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        self.history_panel.grid_columnconfigure(0, weight=1)
        self.history_panel.grid_rowconfigure(1, weight=1)

        self.lbl_hist_title = ctk.CTkLabel(
            self.history_panel, 
            text="Últimas Facturas Generadas", 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.lbl_hist_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        self.history_scroll = ctk.CTkScrollableFrame(self.history_panel)
        self.history_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 15))
        self.history_scroll.grid_columnconfigure(0, weight=1)

        # Exportación de datos (Derecha)
        self.export_panel = ctk.CTkFrame(self.bottom_frame)
        self.export_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        self.export_panel.grid_columnconfigure(0, weight=1)

        self.lbl_exp_title = ctk.CTkLabel(
            self.export_panel, 
            text="Exportación de Históricos", 
            font=ctk.CTkFont(size=15, weight="bold")
        )
        self.lbl_exp_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Botones de exportación
        self.btn_exp_inv_xls = ctk.CTkButton(
            self.export_panel, 
            text="Exportar Facturas a Excel (.xlsx)", 
            command=lambda: self.trigger_export("invoices", "excel"),
            fg_color="#319795",
            hover_color="#234E52",
            height=35
        )
        self.btn_exp_inv_xls.grid(row=1, column=0, sticky="ew", padx=15, pady=10)

        self.btn_exp_inv_csv = ctk.CTkButton(
            self.export_panel, 
            text="Exportar Facturas a CSV (.csv)", 
            command=lambda: self.trigger_export("invoices", "csv"),
            fg_color="#4A5568",
            hover_color="#2D3748",
            height=35
        )
        self.btn_exp_inv_csv.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

        self.btn_exp_time_xls = ctk.CTkButton(
            self.export_panel, 
            text="Exportar Registro de Horas a Excel (.xlsx)", 
            command=lambda: self.trigger_export("time", "excel"),
            fg_color="#2B6CB0",
            hover_color="#1A365D",
            height=35
        )
        self.btn_exp_time_xls.grid(row=3, column=0, sticky="ew", padx=15, pady=10)

        self.btn_exp_time_csv = ctk.CTkButton(
            self.export_panel, 
            text="Exportar Registro de Horas a CSV (.csv)", 
            command=lambda: self.trigger_export("time", "csv"),
            fg_color="#4A5568",
            hover_color="#2D3748",
            height=35
        )
        self.btn_exp_time_csv.grid(row=4, column=0, sticky="ew", padx=15, pady=10)

        # Cargar valores iniciales
        self.refresh()

    def create_kpi_card(self, parent, title, value, accent_color, col_idx) -> tuple[ctk.CTkLabel, ctk.CTkLabel]:
        """Crea una tarjeta KPI modular y estilizada."""
        card = ctk.CTkFrame(parent)
        card.grid(row=0, column=col_idx, padx=8, pady=5, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        # Barra de color estético de acento superior
        accent_bar = ctk.CTkFrame(card, height=4, fg_color=accent_color, corner_radius=0)
        accent_bar.grid(row=0, column=0, sticky="ew")

        # Título de la tarjeta
        lbl_title = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color="gray")
        lbl_title.grid(row=1, column=0, sticky="w", padx=15, pady=(12, 5))

        # Valor numérico principal
        lbl_value = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        lbl_value.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 15))

        return lbl_title, lbl_value

    def refresh(self):
        """Consulta la base de datos y actualiza los resúmenes y el historial de facturas."""
        try:
            # 1. Obtener estadísticas de base de datos
            stats = Invoice.get_statistics()
            total_clients = len(Client.get_all())

            # 2. Actualizar tarjetas KPI
            self.card_total[1].configure(text=f"{stats['total_facturado']:.2f} €")
            self.card_subtotal[1].configure(text=f"{stats['subtotal_facturado']:.2f} €")
            self.card_invoices[1].configure(text=str(stats['numero_facturas']))
            self.card_clients[1].configure(text=str(total_clients))

            # 3. Rellenar historial de facturas
            self.populate_history()

        except Exception as e:
            messagebox.showerror("Error", f"Error al refrescar el Dashboard: {e}")

    def populate_history(self):
        """Obtiene y renderiza las facturas emitidas recientemente."""
        # Limpiar
        for widget in self.history_scroll.winfo_children():
            widget.destroy()

        try:
            invoices = Invoice.get_extended_invoices()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial del dashboard: {e}")
            return

        if not invoices:
            lbl_empty = ctk.CTkLabel(
                self.history_scroll, 
                text="No se han emitido facturas todavía.", 
                font=ctk.CTkFont(slant="italic")
            )
            lbl_empty.grid(row=0, column=0, pady=25)
            return

        # Renderizar lista
        for idx, inv in enumerate(invoices):
            bg_color = ("#F7FAFC", "#2D3748") if idx % 2 == 0 else ("#EDF2F7", "#1A202C")
            inv_frame = ctk.CTkFrame(self.history_scroll, fg_color=bg_color, corner_radius=4)
            inv_frame.grid(row=idx, column=0, sticky="ew", pady=2, padx=2)
            inv_frame.grid_columnconfigure(0, weight=1)
            inv_frame.grid_columnconfigure(1, weight=0)

            # Información
            info_text = f"Factura: {inv['invoice_number']} | Cliente: {inv['client_name']}\nFecha: {inv['issue_date']} | Total: {inv['total']:.2f} €"
            lbl_info = ctk.CTkLabel(inv_frame, text=info_text, justify="left", font=ctk.CTkFont(size=11))
            lbl_info.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            # Botón Abrir PDF (si tiene ruta válida)
            if inv["pdf_path"] and os.path.exists(inv["pdf_path"]):
                btn_open = ctk.CTkButton(
                    inv_frame, 
                    text="Ver PDF", 
                    width=65, 
                    height=24,
                    fg_color="#2B6CB0",
                    hover_color="#1A365D",
                    command=lambda p=inv["pdf_path"]: self.open_pdf(p)
                )
                btn_open.grid(row=0, column=1, sticky="e", padx=10, pady=5)
            else:
                lbl_no_pdf = ctk.CTkLabel(inv_frame, text="Sin PDF", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray")
                lbl_no_pdf.grid(row=0, column=1, sticky="e", padx=10, pady=5)

    def open_pdf(self, path):
        """Abre el archivo PDF usando la herramienta por defecto del sistema operativo."""
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo PDF:\n{e}")

    def trigger_export(self, datatype: str, file_format: str):
        """Abre un diálogo de guardado y ejecuta la exportación seleccionada."""
        if file_format == "excel":
            filetypes = [("Archivos Excel", "*.xlsx")]
            def_ext = ".xlsx"
        else:
            filetypes = [("Archivos CSV", "*.csv")]
            def_ext = ".csv"

        title_msg = f"Exportar Historial de {'Facturas' if datatype == 'invoices' else 'Horas'}"
        default_filename = f"Historico_{'Facturas' if datatype == 'invoices' else 'Horas'}{def_ext}"

        filepath = filedialog.asksaveasfilename(
            title=title_msg,
            initialfile=default_filename,
            defaultextension=def_ext,
            filetypes=filetypes
        )

        if not filepath:
            # Canceló el guardado
            return

        try:
            if datatype == "invoices":
                ExcelExporter.export_invoices(filepath, file_format)
            else:
                ExcelExporter.export_time_logs(filepath, file_format)
            
            messagebox.showinfo("Exportación Completada", f"Los datos han sido exportados correctamente a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"No se pudieron exportar los datos: {e}")
