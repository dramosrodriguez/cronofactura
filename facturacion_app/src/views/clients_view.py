import customtkinter as ctk
from tkinter import messagebox
from src.controllers.client_controller import ClientController

class ClientsView(ctk.CTkFrame):
    """Vista para el ABM (Alta, Baja, Modificación) de Clientes."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.editing_client_id = None  # Almacena el ID del cliente que se está editando

        # --- SECCIÓN IZQUIERDA: FORMULARIO ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=20)
        self.form_frame.grid_columnconfigure(1, weight=1)

        self.form_title = ctk.CTkLabel(
            self.form_frame, 
            text="Registrar Nuevo Cliente", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Nombre
        self.lbl_name = ctk.CTkLabel(self.form_frame, text="Nombre del Cliente:")
        self.lbl_name.grid(row=1, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_name = ctk.CTkEntry(self.form_frame, placeholder_text="Nombre o Razón Social")
        self.ent_name.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=10)

        # NIF
        self.lbl_nif = ctk.CTkLabel(self.form_frame, text="NIF / DNI:")
        self.lbl_nif.grid(row=2, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_nif = ctk.CTkEntry(self.form_frame, placeholder_text="Ej. A1234567B o 12345678X")
        self.ent_nif.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Tarifa Horaria
        self.lbl_rate = ctk.CTkLabel(self.form_frame, text="Tarifa Horaria (€/h):")
        self.lbl_rate.grid(row=3, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_rate = ctk.CTkEntry(self.form_frame, placeholder_text="Ej. 25.0")
        self.ent_rate.grid(row=3, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Email
        self.lbl_email = ctk.CTkLabel(self.form_frame, text="Email:")
        self.lbl_email.grid(row=4, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_email = ctk.CTkEntry(self.form_frame, placeholder_text="Ej. cliente@empresa.com")
        self.ent_email.grid(row=4, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Dirección
        self.lbl_address = ctk.CTkLabel(self.form_frame, text="Dirección:")
        self.lbl_address.grid(row=5, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_address = ctk.CTkEntry(self.form_frame, placeholder_text="Dirección física completa")
        self.ent_address.grid(row=5, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Botones de Formulario
        self.btn_save = ctk.CTkButton(
            self.form_frame, 
            text="Guardar Cliente", 
            command=self.save_client,
            fg_color="#2B6CB0",
            hover_color="#1A365D",
            font=ctk.CTkFont(weight="bold")
        )
        self.btn_save.grid(row=6, column=0, columnspan=2, pady=(15, 5), padx=15, sticky="ew")

        self.btn_cancel = ctk.CTkButton(
            self.form_frame, 
            text="Cancelar Edición", 
            command=self.cancel_edit,
            fg_color="gray",
            hover_color="darkgray"
        )
        # Oculto por defecto, solo se muestra en edición
        self.btn_cancel.grid_remove()

        # --- SECCIÓN DERECHA: LISTA DE CLIENTES ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=20)
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(1, weight=1)

        self.list_title = ctk.CTkLabel(
            self.list_frame, 
            text="Clientes Registrados", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.list_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        # Contenedor con Scroll para la grilla
        self.scroll_frame = ctk.CTkScrollableFrame(self.list_frame)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=2)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        self.scroll_frame.grid_columnconfigure(2, weight=1)
        self.scroll_frame.grid_columnconfigure(3, weight=1)

        # Cargar clientes en la UI
        self.refresh_client_list()

    def refresh_client_list(self):
        """Limpia y vuelve a rellenar la lista de clientes."""
        # Limpiar elementos previos
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # Agregar encabezados de columna estéticos
        headers = ["Cliente / NIF", "Tarifa / Email", "Acciones"]
        for i, header in enumerate(headers):
            # Calculamos columnas en grid
            col = 0 if i == 0 else (1 if i == 1 else 2)
            span = 1
            if i == 2:
                span = 2  # Botones editar y eliminar
            
            lbl = ctk.CTkLabel(
                self.scroll_frame, 
                text=header, 
                font=ctk.CTkFont(weight="bold"),
                text_color=("#2B6CB0", "#90CDF4")
            )
            lbl.grid(row=0, column=col, columnspan=span, sticky="w", padx=10, pady=(5, 10))

        try:
            clients = ClientController.list_clients()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los clientes: {e}")
            return

        if not clients:
            lbl_empty = ctk.CTkLabel(self.scroll_frame, text="No hay clientes registrados.", font=ctk.CTkFont(slant="italic"))
            lbl_empty.grid(row=1, column=0, columnspan=4, pady=20)
            return

        for idx, client in enumerate(clients):
            row_idx = idx + 1
            
            # Verificar si el cliente tiene todos los datos necesarios para facturar
            is_complete = bool(
                client.name and client.name.strip() and
                client.nif and client.nif.strip() and not client.nif.startswith("PENDIENTE-") and
                client.email and client.email.strip() and
                client.address and client.address.strip() and
                client.hourly_rate > 0
            )

            # Formatear la fila (amarillo si está incompleto)
            if not is_complete:
                bg_color = ("#FEFCBF", "#744210")
                text_color = ("#744210", "white")
            else:
                bg_color = ("#F7FAFC", "#2D3748") if idx % 2 == 0 else ("#EDF2F7", "#1A202C")
                text_color = None

            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color=bg_color, corner_radius=4)
            row_frame.grid(row=row_idx, column=0, columnspan=4, sticky="ew", pady=2, padx=2)
            row_frame.grid_columnconfigure(0, weight=2)
            row_frame.grid_columnconfigure(1, weight=2)
            row_frame.grid_columnconfigure(2, weight=0)
            row_frame.grid_columnconfigure(3, weight=0)

            # Col 0: Nombre y NIF (limpiando placeholder)
            nif_display = "[Pendiente]" if client.nif.startswith("PENDIENTE-") or not client.nif else client.nif
            name_text = f"{client.name}\nNIF: {nif_display}"
            lbl_name = ctk.CTkLabel(row_frame, text=name_text, justify="left", font=ctk.CTkFont(size=12), text_color=text_color)
            lbl_name.grid(row=0, column=0, sticky="w", padx=10, pady=5)

            # Col 1: Tarifa e Email (mostrando Pendiente si está vacío)
            email_display = client.email if client.email else "[Pendiente]"
            info_text = f"Tarifa: {client.hourly_rate:.2f} €/h\nEmail: {email_display}"
            lbl_info = ctk.CTkLabel(row_frame, text=info_text, justify="left", font=ctk.CTkFont(size=12), text_color=text_color)
            lbl_info.grid(row=0, column=1, sticky="w", padx=10, pady=5)

            # Col 2: Botón Editar
            btn_edit = ctk.CTkButton(
                row_frame, 
                text="Editar", 
                width=60, 
                height=24,
                fg_color="#D69E2E",
                hover_color="#B7791F",
                command=lambda c=client: self.start_edit(c)
            )
            btn_edit.grid(row=0, column=2, padx=5, pady=5, sticky="e")

            # Col 3: Botón Eliminar
            btn_delete = ctk.CTkButton(
                row_frame, 
                text="Eliminar", 
                width=60, 
                height=24,
                fg_color="#E53E3E",
                hover_color="#C53030",
                command=lambda c=client: self.delete_client(c)
            )
            btn_delete.grid(row=0, column=3, padx=10, pady=5, sticky="e")

    def save_client(self):
        """Inserta o actualiza un cliente tras validar campos."""
        name = self.ent_name.get().strip()
        nif = self.ent_nif.get().strip().upper()
        rate_str = self.ent_rate.get().strip()
        email = self.ent_email.get().strip()
        address = self.ent_address.get().strip()

        # Nombre es el único campo estrictamente obligatorio para crear el registro
        if not name:
            messagebox.showerror("Error de Validación", "El nombre del cliente es obligatorio.")
            return

        # Advertencia de campos vacíos
        if not nif or not rate_str or not email or not address:
            confirm = messagebox.askyesno(
                "Datos Incompletos",
                "Hay campos vacíos (NIF, tarifa, email o dirección). ¿Desea continuar registrando el cliente de todas formas?"
            )
            if not confirm:
                return

        # Validar tarifa numérica si se proporciona
        rate = 0.0
        if rate_str:
            try:
                rate = float(rate_str)
                if rate < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error de Validación", "La tarifa horaria debe ser un número positivo.")
                return

        try:
            if self.editing_client_id:
                # Caso Edición
                ClientController.update_client(
                    client_id=self.editing_client_id,
                    name=name,
                    nif=nif,
                    hourly_rate=rate,
                    email=email,
                    address=address
                )
                messagebox.showinfo("Cliente Actualizado", "El cliente se ha actualizado satisfactoriamente.")
            else:
                # Caso Creación
                ClientController.create_client(
                    name=name,
                    nif=nif,
                    hourly_rate=rate,
                    email=email,
                    address=address
                )
                messagebox.showinfo("Cliente Registrado", "El cliente se ha guardado satisfactoriamente.")
            
            # Limpiar y recargar
            self.clear_form()
            self.refresh_client_list()

        except ValueError as ve:
            messagebox.showerror("Error de Validación", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al procesar: {e}")

    def start_edit(self, client):
        """Carga la información del cliente seleccionado en el formulario para editar."""
        self.editing_client_id = client.id
        self.form_title.configure(text=f"Editar Cliente: {client.name}")
        
        self.ent_name.delete(0, ctk.END)
        self.ent_name.insert(0, client.name)

        self.ent_nif.delete(0, ctk.END)
        if not client.nif.startswith("PENDIENTE-"):
            self.ent_nif.insert(0, client.nif)

        self.ent_rate.delete(0, ctk.END)
        self.ent_rate.insert(0, str(client.hourly_rate))

        self.ent_email.delete(0, ctk.END)
        self.ent_email.insert(0, client.email)

        self.ent_address.delete(0, ctk.END)
        self.ent_address.insert(0, client.address)

        # Cambiar el texto del botón y mostrar el botón de cancelar
        self.btn_save.configure(text="Actualizar Cliente", fg_color="#D69E2E", hover_color="#B7791F")
        self.btn_cancel.grid(row=7, column=0, columnspan=2, pady=(5, 10), padx=15, sticky="ew")

    def cancel_edit(self):
        """Cancela la edición actual y restablece el formulario."""
        self.clear_form()

    def clear_form(self):
        """Limpia los campos del formulario de entrada."""
        self.editing_client_id = None
        self.form_title.configure(text="Registrar Nuevo Cliente")
        self.ent_name.delete(0, ctk.END)
        self.ent_nif.delete(0, ctk.END)
        self.ent_rate.delete(0, ctk.END)
        self.ent_email.delete(0, ctk.END)
        self.ent_address.delete(0, ctk.END)
        self.btn_save.configure(text="Guardar Cliente", fg_color="#2B6CB0", hover_color="#1A365D")
        self.btn_cancel.grid_remove()

    def delete_client(self, client):
        """Confirma y elimina el cliente seleccionado, manejando restricciones relacionales."""
        confirm = messagebox.askyesno(
            "Confirmar Eliminación", 
            f"¿Está seguro de que desea eliminar al cliente {client.name}?\nEsta acción no se puede deshacer."
        )
        if not confirm:
            return

        try:
            ClientController.delete_client(client.id)
            messagebox.showinfo("Cliente Eliminado", f"El cliente {client.name} fue eliminado con éxito.")
            
            # Si estábamos editando este mismo cliente, cancelamos la edición
            if self.editing_client_id == client.id:
                self.clear_form()
                
            self.refresh_client_list()
        except RuntimeError as re:
            # En la BD se levantará error debido a la FK RESTRICT si el cliente tiene registros
            messagebox.showerror(
                "Restricción de Integridad", 
                "No es posible eliminar al cliente porque tiene facturas o registros de tiempo asociados."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al intentar eliminar: {e}")
