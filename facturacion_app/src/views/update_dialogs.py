import customtkinter as ctk
import webbrowser

class UpdateDialog(ctk.CTkToplevel):
    """Ventana modal premium para avisar al usuario de que hay una nueva versión disponible,
    mostrar notas de lanzamiento y confirmar la instalación.
    """
    def __init__(self, parent, version_info, on_confirm):
        super().__init__(parent)
        self.title("Actualización de Software")
        self.geometry("520x490")
        self.resizable(False, False)
        
        self.on_confirm = on_confirm
        self.version_info = version_info
        
        # Centrar con respecto al padre
        if parent:
            self.transient(parent)
            parent.update_idletasks()
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 260
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 245
            self.geometry(f"+{x}+{y}")
            
        self.grab_set()
        self.focus_set()
        
        # Forzar que esté al frente
        self.lift()
        
        # Configurar la cuadricula
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Título / Cabecera
        self.header_label = ctk.CTkLabel(
            self,
            text="¡Nueva Versión Disponible!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1A365D", "#90CDF4")
        )
        self.header_label.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="w")
        
        # Información comparativa de versiones
        current_v = version_info.get("current_version", "0.0.0")
        new_v = version_info.get("new_version", "0.0.0")
        
        info_text = (
            f"Se ha detectado la versión {new_v} en GitHub. Tu versión actual es v{current_v}.\n"
            f"Para más información sobre la actualización, dirígete al enlace de la última versión (latest release) del repositorio:\n"
        )
        
        self.info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ctk.CTkFont(size=13),
            wraplength=470,
            justify="left"
        )
        self.info_label.grid(row=1, column=0, padx=25, pady=(0, 5), sticky="w")

        # Enlace clickable
        self.link_label = ctk.CTkLabel(
            self,
            text="https://github.com/dramosrodriguez/cronofactura/releases/latest",
            font=ctk.CTkFont(size=13, underline=True),
            text_color=("#2B6CB0", "#90CDF4"),
            cursor="hand2"
        )
        self.link_label.grid(row=2, column=0, padx=25, pady=(0, 15), sticky="w")
        self.link_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/dramosrodriguez/cronofactura/releases/latest"))
        
        # Contenedor de notas de versión
        self.notes_frame = ctk.CTkFrame(self)
        self.notes_frame.grid(row=3, column=0, padx=25, pady=(0, 20), sticky="nsew")
        self.notes_frame.grid_columnconfigure(0, weight=1)
        self.notes_frame.grid_rowconfigure(1, weight=1)
        
        self.notes_title = ctk.CTkLabel(
            self.notes_frame,
            text="Notas de la versión:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        )
        self.notes_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.notes_text = ctk.CTkTextbox(self.notes_frame, wrap="word", font=ctk.CTkFont(size=12))
        self.notes_text.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        notes_content = version_info.get("body", "").strip()
        if not notes_content:
            notes_content = "No se han proporcionado notas de lanzamiento para esta versión."
        self.notes_text.insert("1.0", notes_content)
        self.notes_text.configure(state="disabled")
        
        # Botonera
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=4, column=0, padx=25, pady=(0, 25), sticky="ew")
        self.btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.btn_cancel = ctk.CTkButton(
            self.btn_frame,
            text="Más tarde",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            text_color=("#2B6CB0", "#90CDF4"),
            hover_color=("#EDF2F7", "#2D3748"),
            border_width=1,
            border_color=("#2B6CB0", "#90CDF4"),
            height=38,
            command=self.destroy
        )
        self.btn_cancel.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.btn_update = ctk.CTkButton(
            self.btn_frame,
            text="Actualizar ahora",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2B6CB0",
            hover_color="#1A365D",
            height=38,
            command=self.confirm_update
        )
        self.btn_update.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def confirm_update(self):
        self.destroy()
        self.on_confirm()


class DownloadProgressDialog(ctk.CTkToplevel):
    """Ventana modal que muestra el progreso de descarga de la nueva versión.
    Bloquea las acciones de la ventana principal y deshabilita su propio cierre.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Descargando Actualización")
        self.geometry("400x160")
        self.resizable(False, False)
        
        # Centrar con respecto al padre
        if parent:
            self.transient(parent)
            parent.update_idletasks()
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 200
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 80
            self.geometry(f"+{x}+{y}")
            
        self.grab_set()
        self.focus_set()
        
        # Forzar estar al frente
        self.lift()
        
        # Impedir el cierre de la ventana con el botón "X"
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="Descargando actualización desde GitHub...",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.status_label.grid(row=0, column=0, padx=25, pady=(25, 10), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self, width=350)
        self.progress_bar.grid(row=1, column=0, padx=25, pady=(5, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.progress_label.grid(row=2, column=0, padx=25, pady=(0, 20), sticky="e")

    def update_progress(self, percent, bytes_downloaded):
        """Actualiza la barra de progreso y las etiquetas de texto de estado."""
        # Convertir bytes descargados a Megabytes (MB)
        mb_downloaded = bytes_downloaded / (1024 * 1024)
        
        if percent is not None:
            self.progress_bar.set(percent)
            percent_str = f"{int(percent * 100)}%"
            self.status_label.configure(text=f"Descargando actualización... ({mb_downloaded:.2f} MB)")
            self.progress_label.configure(text=percent_str)
        else:
            # Si el tamaño total no está definido, usamos una animación indeterminada
            self.progress_bar.configure(mode="indetermined")
            self.progress_bar.start()
            self.status_label.configure(text=f"Descargando actualización... ({mb_downloaded:.2f} MB)")
            self.progress_label.configure(text="Descargando...")
