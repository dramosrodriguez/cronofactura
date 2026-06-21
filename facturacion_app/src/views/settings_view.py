import os
import json
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Buscar la ruta absoluta del archivo settings.json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")

class SettingsView(ctk.CTkFrame):
    """Vista de configuración del emisor y tasas de impuestos."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Contenedor con scroll por si la pantalla se reduce
        self.scrollable_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scrollable_container.grid_columnconfigure(0, weight=1)
        # Contenedor del título y versión del proyecto
        self.header_frame = ctk.CTkFrame(self.scrollable_container, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)

        # Título de la vista
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Configuración del Emisor e Impuestos", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1A365D", "#90CDF4")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Etiqueta de versión
        from src import __version__
        self.version_label = ctk.CTkLabel(
            self.header_frame,
            text=f"v{__version__}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#319795", "#4FD1C5")  # Color verde azulado / teal distintivo
        )
        self.version_label.grid(row=0, column=1, sticky="e", padx=(10, 5), pady=(5, 0))

        # --- SECCIÓN DATOS FISCALES ---
        self.emisor_frame = ctk.CTkFrame(self.scrollable_container)
        self.emisor_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20), padx=5)
        self.emisor_frame.grid_columnconfigure(1, weight=1)

        self.emisor_title = ctk.CTkLabel(
            self.emisor_frame, 
            text="Datos Fiscales del Autónomo (Emisor)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.emisor_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # Nombre
        self.lbl_nombre = ctk.CTkLabel(self.emisor_frame, text="Nombre Completo / Razón Social:")
        self.lbl_nombre.grid(row=1, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_nombre = ctk.CTkEntry(self.emisor_frame, placeholder_text="Ej. Juan Pérez García")
        self.ent_nombre.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=10)

        # NIF/CIF
        self.lbl_nif = ctk.CTkLabel(self.emisor_frame, text="NIF / DNI / CIF:")
        self.lbl_nif.grid(row=2, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_nif = ctk.CTkEntry(self.emisor_frame, placeholder_text="Ej. 12345678Z")
        self.ent_nif.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Dirección
        self.lbl_direccion = ctk.CTkLabel(self.emisor_frame, text="Dirección Fiscal Completa:")
        self.lbl_direccion.grid(row=3, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_direccion = ctk.CTkEntry(self.emisor_frame, placeholder_text="Ej. Calle Mayor 12, 3º B, Madrid")
        self.ent_direccion.grid(row=3, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Email
        self.lbl_email = ctk.CTkLabel(self.emisor_frame, text="Email de Contacto:")
        self.lbl_email.grid(row=4, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_email = ctk.CTkEntry(self.emisor_frame, placeholder_text="Ej. juan.perez@email.com")
        self.ent_email.grid(row=4, column=1, sticky="ew", padx=(0, 15), pady=10)

        # Cuenta Bancaria
        self.lbl_cuenta = ctk.CTkLabel(self.emisor_frame, text="Cuenta Bancaria (IBAN):")
        self.lbl_cuenta.grid(row=5, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_cuenta = ctk.CTkEntry(self.emisor_frame, placeholder_text="Ej. ES12 3456 7890 1234 5678 9012")
        self.ent_cuenta.grid(row=5, column=1, sticky="ew", padx=(0, 15), pady=10)

        # --- SECCIÓN TASAS DE IMPUESTOS POR DEFECTO ---
        self.tax_frame = ctk.CTkFrame(self.scrollable_container)
        self.tax_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20), padx=5)
        self.tax_frame.grid_columnconfigure(1, weight=1)

        self.tax_title = ctk.CTkLabel(
            self.tax_frame, 
            text="Tasas de Impuestos Predeterminadas", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.tax_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        # IVA
        self.lbl_iva = ctk.CTkLabel(self.tax_frame, text="I.V.A. Defecto (%):")
        self.lbl_iva.grid(row=1, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_iva = ctk.CTkEntry(self.tax_frame, placeholder_text="Ej. 21.0")
        self.ent_iva.grid(row=1, column=1, sticky="ew", padx=(0, 15), pady=10)

        # IRPF
        self.lbl_irpf = ctk.CTkLabel(self.tax_frame, text="I.R.P.F. Defecto (%):")
        self.lbl_irpf.grid(row=2, column=0, sticky="e", padx=(15, 10), pady=10)
        self.ent_irpf = ctk.CTkEntry(self.tax_frame, placeholder_text="Ej. 15.0")
        self.ent_irpf.grid(row=2, column=1, sticky="ew", padx=(0, 15), pady=10)

        # --- SECCIÓN CARPETA DESTINO DE FACTURAS ---
        self.path_frame = ctk.CTkFrame(self.scrollable_container)
        self.path_frame.grid(row=3, column=0, sticky="ew", pady=(0, 20), padx=5)
        self.path_frame.grid_columnconfigure(1, weight=1)
        self.path_frame.grid_columnconfigure(2, weight=0)

        self.path_title = ctk.CTkLabel(
            self.path_frame, 
            text="Carpeta de Guardado de Facturas (PDF)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.path_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(15, 10))

        self.lbl_ruta = ctk.CTkLabel(self.path_frame, text="Ruta Destino:")
        self.lbl_ruta.grid(row=1, column=0, sticky="e", padx=(15, 10), pady=10)

        self.ent_ruta_facturas = ctk.CTkEntry(self.path_frame, placeholder_text="Por defecto (facturas_emitidas/)")
        self.ent_ruta_facturas.grid(row=1, column=1, sticky="ew", pady=10)

        self.btn_select_path = ctk.CTkButton(
            self.path_frame, 
            text="Examinar...", 
            width=80, 
            command=self.select_output_directory
        )
        self.btn_select_path.grid(row=1, column=2, padx=(10, 15), pady=10)

        # --- SECCIÓN CARPETA DESTINO DE INFORMES ---
        self.reports_path_frame = ctk.CTkFrame(self.scrollable_container)
        self.reports_path_frame.grid(row=4, column=0, sticky="ew", pady=(0, 20), padx=5)
        self.reports_path_frame.grid_columnconfigure(1, weight=1)
        self.reports_path_frame.grid_columnconfigure(2, weight=0)

        self.reports_path_title = ctk.CTkLabel(
            self.reports_path_frame, 
            text="Carpeta de Guardado de Informes (PDF)", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.reports_path_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(15, 10))

        self.lbl_ruta_informes = ctk.CTkLabel(self.reports_path_frame, text="Ruta Destino:")
        self.lbl_ruta_informes.grid(row=1, column=0, sticky="e", padx=(15, 10), pady=10)

        self.ent_ruta_informes = ctk.CTkEntry(self.reports_path_frame, placeholder_text="Por defecto (informes/)")
        self.ent_ruta_informes.grid(row=1, column=1, sticky="ew", pady=10)

        self.btn_select_reports_path = ctk.CTkButton(
            self.reports_path_frame, 
            text="Examinar...", 
            width=80, 
            command=self.select_reports_output_directory
        )
        self.btn_select_reports_path.grid(row=1, column=2, padx=(10, 15), pady=10)

        # --- SECCIÓN ACTUALIZACIONES DE LA APLICACIÓN ---
        self.updates_frame = ctk.CTkFrame(self.scrollable_container)
        self.updates_frame.grid(row=5, column=0, sticky="ew", pady=(0, 20), padx=5)
        self.updates_frame.grid_columnconfigure(0, weight=1)

        self.updates_title = ctk.CTkLabel(
            self.updates_frame, 
            text="Actualizaciones de Software", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.updates_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))

        self.switch_updates = ctk.CTkSwitch(
            self.updates_frame,
            text="Buscar nuevas versiones al iniciar la aplicación",
            font=ctk.CTkFont(size=13)
        )
        self.switch_updates.grid(row=1, column=0, sticky="w", padx=15, pady=(5, 15))

        # --- BOTÓN GUARDAR Y ESTADO ---
        self.btn_guardar = ctk.CTkButton(
            self.scrollable_container, 
            text="Guardar Configuración", 
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.save_settings,
            height=40,
            fg_color="#2B6CB0",
            hover_color="#1A365D"
        )
        self.btn_guardar.grid(row=6, column=0, pady=(10, 20), padx=5, sticky="ew")

        self.lbl_status = ctk.CTkLabel(self.scrollable_container, text="", font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_status.grid(row=7, column=0, pady=(0, 10))

        # Cargar valores iniciales
        self.load_settings()

    def load_settings(self):
        """Carga las configuraciones del archivo settings.json."""
        if not os.path.exists(SETTINGS_PATH):
            return

        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            emisor = config.get("emisor", {})
            self.ent_nombre.delete(0, ctk.END)
            self.ent_nombre.insert(0, emisor.get("nombre", ""))
            
            self.ent_nif.delete(0, ctk.END)
            self.ent_nif.insert(0, emisor.get("nif", ""))
            
            self.ent_direccion.delete(0, ctk.END)
            self.ent_direccion.insert(0, emisor.get("direccion", ""))
            
            self.ent_email.delete(0, ctk.END)
            self.ent_email.insert(0, emisor.get("email", ""))

            self.ent_cuenta.delete(0, ctk.END)
            self.ent_cuenta.insert(0, emisor.get("cuenta_bancaria", ""))

            impuestos = config.get("impuestos_defecto", {})
            self.ent_iva.delete(0, ctk.END)
            self.ent_iva.insert(0, str(impuestos.get("iva_porcentaje", 21.0)))
            
            self.ent_irpf.delete(0, ctk.END)
            self.ent_irpf.insert(0, str(impuestos.get("irpf_porcentaje", 15.0)))
            
            self.ent_ruta_facturas.delete(0, ctk.END)
            self.ent_ruta_facturas.insert(0, config.get("ruta_facturas", ""))
            
            self.ent_ruta_informes.delete(0, ctk.END)
            self.ent_ruta_informes.insert(0, config.get("ruta_informes", ""))
            
            # Cargar estado de buscar_actualizaciones
            buscar_actualizaciones = config.get("buscar_actualizaciones", True)
            if buscar_actualizaciones:
                self.switch_updates.select()
            else:
                self.switch_updates.deselect()
            
            self.show_status("Configuración cargada correctamente.", "green")
        except Exception as e:
            self.show_status("Error al cargar configuraciones.", "red")
            messagebox.showerror("Error", f"No se pudo cargar la configuración: {e}")

    def save_settings(self):
        """Guarda la configuración usando un patrón de escritura atómica."""
        nombre = self.ent_nombre.get().strip()
        nif = self.ent_nif.get().strip().upper()
        direccion = self.ent_direccion.get().strip()
        email = self.ent_email.get().strip()
        cuenta_bancaria = self.ent_cuenta.get().strip()
        iva_str = self.ent_iva.get().strip()
        irpf_str = self.ent_irpf.get().strip()
        ruta_facturas = self.ent_ruta_facturas.get().strip()
        ruta_informes = self.ent_ruta_informes.get().strip()

        # Validación en Frontend
        if not nombre or not nif or not direccion or not email or not cuenta_bancaria:
            messagebox.showerror("Error de Validación", "Todos los campos de datos fiscales y bancarios son obligatorios.")
            return

        # Si se especifica una ruta, verificar si se puede crear/acceder
        if ruta_facturas:
            try:
                os.makedirs(ruta_facturas, exist_ok=True)
            except Exception:
                messagebox.showerror("Error de Validación", "La ruta de guardado de facturas especificada no es válida o no se puede crear.")
                return

        # Si se especifica una ruta de informes, verificar si se puede crear/acceder
        if ruta_informes:
            try:
                os.makedirs(ruta_informes, exist_ok=True)
            except Exception:
                messagebox.showerror("Error de Validación", "La ruta de guardado de informes especificada no es válida o no se puede crear.")
                return

        try:
            iva_val = float(iva_str)
            irpf_val = float(irpf_str)
            if iva_val < 0 or irpf_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error de Validación", "Las tasas de impuestos deben ser valores numéricos positivos (Ej. 21.0, 15.0).")
            return

        buscar_actualizaciones = bool(self.switch_updates.get())

        # Cargar configuración existente para preservar otros valores (como apariencia)
        config_data = {}
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
            except Exception:
                pass

        config_data["emisor"] = {
            "nombre": nombre,
            "nif": nif,
            "direccion": direccion,
            "email": email,
            "cuenta_bancaria": cuenta_bancaria
        }
        config_data["impuestos_defecto"] = {
            "iva_porcentaje": iva_val,
            "irpf_porcentaje": irpf_val
        }
        config_data["ruta_facturas"] = ruta_facturas
        config_data["ruta_informes"] = ruta_informes
        config_data["buscar_actualizaciones"] = buscar_actualizaciones

        # Asegurarse de que el directorio del archivo settings.json exista
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        
        # Patrón de Escritura Atómica
        tmp_path = SETTINGS_PATH + ".tmp"
        try:
            # Escribir en archivo temporal
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            # Reemplazar atómicamente el archivo real por el temporal
            if os.path.exists(SETTINGS_PATH):
                os.replace(tmp_path, SETTINGS_PATH)
            else:
                os.rename(tmp_path, SETTINGS_PATH)
                
            self.show_status("¡Configuración guardada con éxito!", "green")
            # Notificar a la app principal para que actualice datos si es necesario
            messagebox.showinfo("Configuración", "Los datos fiscales y de impuestos se han guardado correctamente.")
        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            self.show_status("Error al guardar la configuración.", "red")
            messagebox.showerror("Error", f"No se pudo guardar la configuración: {e}")

    def show_status(self, text, color):
        """Muestra un mensaje de estado en la interfaz."""
        self.lbl_status.configure(text=text, text_color=color)
        # Limpiar mensaje después de 5 segundos
        self.after(5000, lambda: self.lbl_status.configure(text=""))

    def select_output_directory(self):
        """Abre un diálogo de selección de directorio y actualiza la entrada."""
        initial_dir = self.ent_ruta_facturas.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")
            
        directory = filedialog.askdirectory(
            parent=self,
            title="Seleccionar Carpeta para Facturas PDF",
            initialdir=initial_dir
        )
        if directory:
            self.ent_ruta_facturas.delete(0, ctk.END)
            self.ent_ruta_facturas.insert(0, os.path.normpath(directory))

    def select_reports_output_directory(self):
        """Abre un diálogo de selección de directorio para informes y actualiza la entrada."""
        initial_dir = self.ent_ruta_informes.get().strip()
        if not initial_dir or not os.path.exists(initial_dir):
            initial_dir = os.path.expanduser("~")
            
        directory = filedialog.askdirectory(
            parent=self,
            title="Seleccionar Carpeta para Informes PDF",
            initialdir=initial_dir
        )
        if directory:
            self.ent_ruta_informes.delete(0, ctk.END)
            self.ent_ruta_informes.insert(0, os.path.normpath(directory))
