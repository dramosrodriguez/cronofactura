import os
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from src.controllers.client_controller import ClientController
from src.controllers.time_controller import TimeController
from src.controllers.invoice_controller import InvoiceController

class HistoryView(ctk.CTkFrame):
    """Vista de gestión y consulta del historial de facturas y tareas registradas."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # El listado es flexible verticalmente

        self.clients_map = {}
        self.all_invoices = []
        self.all_logs = []

        # --- FILTROS COMUNES SUPERIORES ---
        self.filters_frame = ctk.CTkFrame(self)
        self.filters_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.filters_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Filtro de Cliente
        self.lbl_client = ctk.CTkLabel(self.filters_frame, text="Cliente:", font=ctk.CTkFont(weight="bold"))
        self.lbl_client.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))
        
        self.cmb_filter_client = ctk.CTkOptionMenu(
            self.filters_frame,
            values=["Todos los clientes"],
            command=lambda x: self.apply_filters()
        )
        self.cmb_filter_client.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Filtro de Fecha Inicio
        self.lbl_start = ctk.CTkLabel(self.filters_frame, text="Desde (YYYY-MM-DD):", font=ctk.CTkFont(weight="bold"))
        self.lbl_start.grid(row=0, column=1, sticky="w", padx=15, pady=(10, 2))
        
        self.start_date_frame = ctk.CTkFrame(self.filters_frame, fg_color="transparent")
        self.start_date_frame.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")
        self.start_date_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_start_date = ctk.CTkEntry(self.start_date_frame, placeholder_text="AAAA-MM-DD")
        self.ent_start_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_date_start = ctk.CTkButton(
            self.start_date_frame,
            text="📅",
            width=32,
            command=lambda: self.open_date_picker(self.ent_start_date)
        )
        self.btn_date_start.grid(row=0, column=1)

        # Filtro de Fecha Fin
        self.lbl_end = ctk.CTkLabel(self.filters_frame, text="Hasta (YYYY-MM-DD):", font=ctk.CTkFont(weight="bold"))
        self.lbl_end.grid(row=0, column=2, sticky="w", padx=15, pady=(10, 2))
        
        self.end_date_frame = ctk.CTkFrame(self.filters_frame, fg_color="transparent")
        self.end_date_frame.grid(row=1, column=2, padx=15, pady=(0, 15), sticky="ew")
        self.end_date_frame.grid_columnconfigure(0, weight=1)
        
        self.ent_end_date = ctk.CTkEntry(self.end_date_frame, placeholder_text="AAAA-MM-DD")
        self.ent_end_date.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_date_end = ctk.CTkButton(
            self.end_date_frame,
            text="📅",
            width=32,
            command=lambda: self.open_date_picker(self.ent_end_date)
        )
        self.btn_date_end.grid(row=0, column=1)

        # Botones de Acción de Filtros
        self.btns_filter_frame = ctk.CTkFrame(self.filters_frame, fg_color="transparent")
        self.btns_filter_frame.grid(row=1, column=3, padx=15, pady=(0, 15), sticky="ew")
        self.btns_filter_frame.grid_columnconfigure((0, 1), weight=1)

        self.btn_apply_filters = ctk.CTkButton(
            self.btns_filter_frame,
            text="Filtrar",
            command=self.apply_filters,
            fg_color="#2B6CB0",
            hover_color="#1A365D",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_apply_filters.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_clear_filters = ctk.CTkButton(
            self.btns_filter_frame,
            text="Limpiar",
            command=self.clear_filters,
            fg_color="#718096",
            hover_color="#4A5568",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_clear_filters.grid(row=0, column=1, padx=(5, 0), sticky="ew")


        # --- CONTENEDOR PRINCIPAL: PESTAÑAS ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.tabview.add("Facturas")
        self.tabview.add("Tareas")

        # Pestaña Facturas Layout
        self.tab_invoices = self.tabview.tab("Facturas")
        self.tab_invoices.grid_columnconfigure(0, weight=1)
        self.tab_invoices.grid_rowconfigure(0, weight=1)
        
        self.invoices_scroll = ctk.CTkScrollableFrame(self.tab_invoices)
        self.invoices_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.invoices_scroll.grid_columnconfigure(0, weight=1)

        # Pestaña Tareas Layout
        self.tab_tasks = self.tabview.tab("Tareas")
        self.tab_tasks.grid_columnconfigure(0, weight=1)
        self.tab_tasks.grid_rowconfigure(1, weight=1)

        # Barra de herramientas superior de tareas
        self.tasks_toolbar = ctk.CTkFrame(self.tab_tasks, fg_color="transparent")
        self.tasks_toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        self.tasks_toolbar.grid_columnconfigure(0, weight=1)
        self.tasks_toolbar.grid_columnconfigure(1, weight=0)

        self.lbl_tasks_summary = ctk.CTkLabel(
            self.tasks_toolbar,
            text="Seleccione un cliente y rango de fechas para exportar el informe.",
            font=ctk.CTkFont(size=12, slant="italic")
        )
        self.lbl_tasks_summary.grid(row=0, column=0, sticky="w")

        self.btn_export_report = ctk.CTkButton(
            self.tasks_toolbar,
            text="📄 Exportar Informe (PDF)",
            command=self.export_progress_report,
            fg_color="#319795",
            hover_color="#234E52",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_export_report.grid(row=0, column=1, sticky="e")

        self.tasks_scroll = ctk.CTkScrollableFrame(self.tab_tasks)
        self.tasks_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.tasks_scroll.grid_columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        """Refresca los clientes, facturas y tareas desde la base de datos."""
        self.load_clients()
        self.load_data()
        self.apply_filters()

    def load_clients(self):
        """Carga los clientes en el combobox de filtrado."""
        try:
            clients = ClientController.list_clients()
            self.clients_map = {client.name: client for client in clients}
            
            names = ["Todos los clientes"] + list(self.clients_map.keys())
            
            # Guardamos la selección actual
            curr_sel = self.cmb_filter_client.get()
            self.cmb_filter_client.configure(values=names)
            if curr_sel in names:
                self.cmb_filter_client.set(curr_sel)
            else:
                self.cmb_filter_client.set("Todos los clientes")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar clientes para filtros: {e}")

    def load_data(self):
        """Carga facturas y logs de horas de la base de datos en caché local."""
        try:
            self.all_invoices = InvoiceController.list_invoices()
            self.all_logs = TimeController.list_logs()
        except Exception as e:
            messagebox.showerror("Error", f"Error al recuperar datos: {e}")

    def open_date_picker(self, entry_widget):
        """Abre el date picker modal."""
        from src.views.date_picker import CTkDatePicker
        val = entry_widget.get().strip()
        
        def handle_selection(date_str):
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, date_str)
            self.apply_filters()
            
        CTkDatePicker(self, callback=handle_selection, start_date_str=val)

    def apply_filters(self):
        """Aplica los filtros de cliente y fechas a ambas listas."""
        client_filter = self.cmb_filter_client.get()
        start_date_str = self.ent_start_date.get().strip()
        end_date_str = self.ent_end_date.get().strip()

        # Validar formato de fechas si no están vacías
        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error de Fecha", "El formato de fecha de inicio debe ser YYYY-MM-DD")
                return

        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error de Fecha", "El formato de fecha de fin debe ser YYYY-MM-DD")
                return

        if start_date and end_date and start_date > end_date:
            messagebox.showerror("Rango Inválido", "La fecha de inicio no puede ser posterior a la fecha de fin.")
            return

        self.render_invoices(client_filter, start_date, end_date)
        self.render_tasks(client_filter, start_date, end_date)

    def clear_filters(self):
        """Limpia los campos de filtro y actualiza las listas."""
        self.cmb_filter_client.set("Todos los clientes")
        self.ent_start_date.delete(0, ctk.END)
        self.ent_end_date.delete(0, ctk.END)
        self.apply_filters()

    def render_invoices(self, client_filter, start_date, end_date):
        """Filtra y renderiza la pestaña de Facturas."""
        # Limpiar
        for widget in self.invoices_scroll.winfo_children():
            widget.destroy()

        filtered_invoices = []
        for inv in self.all_invoices:
            # Filtro por cliente
            if client_filter != "Todos los clientes" and inv["client_name"] != client_filter:
                continue

            # Filtro por fechas (sobre issue_date)
            inv_date = datetime.strptime(inv["issue_date"], "%Y-%m-%d")
            if start_date and inv_date < start_date:
                continue
            if end_date and inv_date > end_date:
                continue

            filtered_invoices.append(inv)

        if not filtered_invoices:
            lbl_empty = ctk.CTkLabel(
                self.invoices_scroll,
                text="No se encontraron facturas con los filtros seleccionados.",
                font=ctk.CTkFont(slant="italic")
            )
            lbl_empty.grid(row=0, column=0, pady=25)
            return

        for idx, inv in enumerate(filtered_invoices):
            bg_color = ("#F7FAFC", "#2D3748") if idx % 2 == 0 else ("#EDF2F7", "#1A202C")
            inv_frame = ctk.CTkFrame(self.invoices_scroll, fg_color=bg_color, corner_radius=6)
            inv_frame.grid(row=idx, column=0, sticky="ew", pady=3, padx=5)
            inv_frame.grid_columnconfigure(0, weight=1)
            inv_frame.grid_columnconfigure(1, weight=0)

            # Contenido informativo principal de la factura
            info_text = (
                f"Factura: {inv['invoice_number']}  |  Cliente: {inv['client_name']}\n"
                f"Fecha Emisión: {inv['issue_date']}  |  Vencimiento: {inv['due_date']}  |  Tipo: {inv['billing_type'].capitalize()}\n"
                f"Base Imponible: {inv['subtotal']:.2f} €  |  IVA ({inv['vat_rate']}%): {inv['vat_amount']:.2f} €  |  IRPF ({inv['irpf_rate']}%): {inv['irpf_amount']:.2f} €  |  Total: {inv['total']:.2f} €"
            )
            
            lbl_info = ctk.CTkLabel(
                inv_frame,
                text=info_text,
                justify="left",
                font=ctk.CTkFont(size=12)
            )
            lbl_info.grid(row=0, column=0, sticky="w", padx=15, pady=8)

            # Frame de botones
            btn_frame = ctk.CTkFrame(inv_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=15, pady=8, sticky="e")

            # Botón Ver PDF
            if inv["pdf_path"] and os.path.exists(inv["pdf_path"]):
                btn_pdf = ctk.CTkButton(
                    btn_frame,
                    text="Ver PDF",
                    width=75,
                    height=26,
                    fg_color="#319795",
                    hover_color="#234E52",
                    command=lambda p=inv["pdf_path"]: self.open_pdf(p)
                )
                btn_pdf.grid(row=0, column=0, padx=(0, 5))
            else:
                lbl_no_pdf = ctk.CTkLabel(
                    btn_frame,
                    text="Sin PDF",
                    font=ctk.CTkFont(size=11, slant="italic"),
                    text_color="gray"
                )
                lbl_no_pdf.grid(row=0, column=0, padx=(0, 10))

            # Botón Eliminar
            btn_del = ctk.CTkButton(
                btn_frame,
                text="Eliminar",
                width=75,
                height=26,
                fg_color="#E53E3E",
                hover_color="#C53030",
                command=lambda i_id=inv["id"], i_num=inv["invoice_number"]: self.delete_invoice(i_id, i_num)
            )
            btn_del.grid(row=0, column=1)

    def render_tasks(self, client_filter, start_date, end_date):
        """Filtra y renderiza la pestaña de Tareas."""
        # Limpiar
        for widget in self.tasks_scroll.winfo_children():
            widget.destroy()

        filtered_logs = []
        for log in self.all_logs:
            # Filtro por cliente
            if client_filter != "Todos los clientes" and log["client_name"] != client_filter:
                continue

            # Filtro por fechas (sobre date)
            log_date = datetime.strptime(log["date"], "%Y-%m-%d")
            if start_date and log_date < start_date:
                continue
            if end_date and log_date > end_date:
                continue

            filtered_logs.append(log)

        total_hours = sum(log["hours"] for log in filtered_logs)
        total_minutes = round(total_hours * 60)
        h_val = total_minutes // 60
        m_val = total_minutes % 60
        time_str = f"{h_val}h {m_val}m" if h_val > 0 else f"{m_val}m"
        
        if client_filter != "Todos los clientes":
            self.lbl_tasks_summary.configure(
                text=f"Cliente: {client_filter} | {len(filtered_logs)} tareas | Total: {time_str} ({total_hours:.2f} h)",
                text_color=("#1A365D", "#90CDF4")
            )
        else:
            self.lbl_tasks_summary.configure(
                text=f"Todos los clientes | {len(filtered_logs)} tareas | Total: {time_str} ({total_hours:.2f} h)",
                text_color=("#4A5568", "#A0AEC0")
            )

        if not filtered_logs:
            lbl_empty = ctk.CTkLabel(
                self.tasks_scroll,
                text="No se encontraron tareas con los filtros seleccionados.",
                font=ctk.CTkFont(slant="italic")
            )
            lbl_empty.grid(row=0, column=0, pady=25)
            return

        for idx, log in enumerate(filtered_logs):
            bg_color = ("#F7FAFC", "#2D3748") if idx % 2 == 0 else ("#EDF2F7", "#1A202C")
            log_frame = ctk.CTkFrame(self.tasks_scroll, fg_color=bg_color, corner_radius=6)
            log_frame.grid(row=idx, column=0, sticky="ew", pady=3, padx=5)
            log_frame.grid_columnconfigure(0, weight=1)
            log_frame.grid_columnconfigure(1, weight=0)

            # Estado de facturación de la tarea
            if log["invoice_id"] is not None:
                billed_status = "Facturado"
                billed_color = "green"
            else:
                billed_status = "Pendiente"
                billed_color = "#B7791F"

            total_minutes = round(log["hours"] * 60)
            h_val = total_minutes // 60
            m_val = total_minutes % 60
            time_str = f"{h_val}h {m_val}m" if h_val > 0 else f"{m_val}m"

            detail_text = (
                f"Fecha: {log['date']}  |  Cliente: {log['client_name']}  |  Tiempo: {time_str} ({log['hours']:.2f} h)\n"
                f"Descripción: {log['description']}"
            )
            if log.get("notes"):
                detail_text += f"\nObservación interna: {log['notes']}"

            # Contenido informativo principal de la tarea
            info_frame = ctk.CTkFrame(log_frame, fg_color="transparent")
            info_frame.grid(row=0, column=0, sticky="w", padx=15, pady=8)
            info_frame.grid_columnconfigure(0, weight=1)

            lbl_detail = ctk.CTkLabel(info_frame, text=detail_text, justify="left", font=ctk.CTkFont(size=12))
            lbl_detail.grid(row=0, column=0, sticky="w")

            # Frame de botones y estado
            btn_frame = ctk.CTkFrame(log_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=1, padx=15, pady=8, sticky="e")

            # Estado badge
            lbl_status = ctk.CTkLabel(
                btn_frame,
                text=billed_status,
                text_color=billed_color,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            lbl_status.grid(row=0, column=0, padx=(0, 15))

            current_col = 1
            if log["invoice_id"] is None:
                # Botón Continuar en Cronómetro
                btn_timer = ctk.CTkButton(
                    btn_frame,
                    text="⏱",
                    width=28,
                    height=26,
                    fg_color="#319795",
                    hover_color="#234E52",
                    command=lambda l=log: self.continue_task_in_timer(l)
                )
                btn_timer.grid(row=0, column=current_col, padx=(0, 5))
                current_col += 1
                
                # Botón Editar
                btn_edit = ctk.CTkButton(
                    btn_frame,
                    text="✏",
                    width=28,
                    height=26,
                    fg_color="#2B6CB0",
                    hover_color="#1A365D",
                    command=lambda l=log: self.continue_task_in_manual(l)
                )
                btn_edit.grid(row=0, column=current_col, padx=(0, 5))
                current_col += 1

            # Botón Eliminar
            btn_del = ctk.CTkButton(
                btn_frame,
                text="Eliminar",
                width=75,
                height=26,
                fg_color="#E53E3E",
                hover_color="#C53030",
                command=lambda l_id=log["id"]: self.delete_task(l_id)
            )
            btn_del.grid(row=0, column=current_col)

    def open_pdf(self, path):
        """Abre un PDF con la aplicación predeterminada del sistema."""
        try:
            os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF:\n{e}")

    def delete_invoice(self, invoice_id: int, invoice_number: str):
        """Lógica de eliminación de facturas con doble confirmación."""
        # Confirmación 1: Diálogo modal
        confirm = messagebox.askyesno(
            "Confirmar Eliminación de Factura",
            f"¿Está seguro de que desea eliminar la factura {invoice_number}?\n\n"
            "Esta acción desvinculará sus tareas asociadas y las volverá a marcar como PENDIENTES. "
            "El archivo PDF generado en el disco no será eliminado. "
            "Esta operación no se puede deshacer."
        )
        if not confirm:
            return

        try:
            success = InvoiceController.delete_invoice(invoice_id)
            if success:
                messagebox.showinfo("Factura Eliminada", f"La factura {invoice_number} ha sido eliminada de la base de datos con éxito.")
                self.refresh()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la factura de la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al intentar eliminar la factura: {e}")

    def delete_task(self, log_id: int):
        """Lógica de eliminación de tareas con doble confirmación."""
        # Confirmación 1: Diálogo modal
        confirm = messagebox.askyesno(
            "Confirmar Eliminación de Tarea",
            "¿Está seguro de que desea eliminar la tarea seleccionada de la base de datos?\n\n"
            "Esta acción no se puede deshacer."
        )
        if not confirm:
            return

        try:
            success = TimeController.delete_log(log_id)
            if success:
                messagebox.showinfo("Tarea Eliminada", "La tarea ha sido eliminada con éxito.")
                self.refresh()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la tarea de la base de datos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al intentar eliminar la tarea: {e}")

    def continue_task_in_timer(self, log):
        """Redirige a la vista de registro cargando la tarea en el cronómetro."""
        main_window = self.winfo_toplevel()
        main_window.select_view("time")
        main_window.views["time"].continue_in_timer(log)

    def continue_task_in_manual(self, log):
        """Redirige a la vista de registro cargando la tarea en el editor manual."""
        main_window = self.winfo_toplevel()
        main_window.select_view("time")
        main_window.views["time"].continue_in_manual(log)

    def export_progress_report(self):
        """Exporta un informe de avances en PDF para el cliente y periodo seleccionados."""
        client_filter = self.cmb_filter_client.get()
        if client_filter == "Todos los clientes":
            messagebox.showwarning(
                "Cliente Requerido",
                "Por favor, seleccione un cliente específico en el filtro superior para exportar su informe de avances."
            )
            return

        start_date_str = self.ent_start_date.get().strip()
        end_date_str = self.ent_end_date.get().strip()
        if not start_date_str or not end_date_str:
            messagebox.showwarning(
                "Rango de Fechas Requerido",
                "Por favor, especifique una fecha de inicio ('Desde') y una fecha de fin ('Hasta') en el filtro superior para exportar el informe."
            )
            return

        # Validar fechas
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror(
                "Error de Fecha",
                "El formato de las fechas de inicio y fin debe ser YYYY-MM-DD (Ej. 2026-06-14)."
            )
            return

        if start_date > end_date:
            messagebox.showerror(
                "Rango Inválido",
                "La fecha de inicio no puede ser posterior a la fecha de fin."
            )
            return

        # Obtener el objeto Cliente
        client = self.clients_map.get(client_filter)
        if not client:
            messagebox.showerror(
                "Cliente no Encontrado",
                f"No se pudieron cargar los datos del cliente: {client_filter}."
            )
            return

        # Filtrar tareas del cliente en el rango seleccionado
        report_logs = []
        for log in self.all_logs:
            if log["client_name"] != client_filter:
                continue
            try:
                log_date = datetime.strptime(log["date"], "%Y-%m-%d")
                if start_date <= log_date <= end_date:
                    report_logs.append(log)
            except ValueError:
                continue

        if not report_logs:
            messagebox.showinfo(
                "Sin Tareas",
                f"No se encontraron tareas registradas para el cliente {client_filter} en el periodo especificado ({start_date_str} a {end_date_str})."
            )
            return

        # Iniciar generación del PDF
        try:
            from src.utils.pdf_generator import ejecutar_generacion_informe_pdf
            
            # Ordenar tareas por fecha ascendente para el informe
            report_logs_sorted = sorted(report_logs, key=lambda x: x["date"])
            
            pdf_path = ejecutar_generacion_informe_pdf(client, report_logs_sorted, start_date_str, end_date_str)
            
            # Confirmación de apertura
            confirm = messagebox.askyesno(
                "Informe Exportado con Éxito",
                f"El informe de avances se ha guardado en:\n{pdf_path}\n\n¿Desea abrir el archivo PDF ahora?"
            )
            if confirm:
                self.open_pdf(pdf_path)
                
        except Exception as e:
            messagebox.showerror(
                "Error al Generar Informe",
                f"Ocurrió un error al generar el PDF del informe:\n{str(e)}"
            )
