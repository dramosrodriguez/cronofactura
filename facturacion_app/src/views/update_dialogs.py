import customtkinter as ctk
import webbrowser
import re

def parse_inline(text, base_tags=None, link_bindings=None):
    if base_tags is None:
        base_tags = ()
    if link_bindings is None:
        link_bindings = []
        
    # Pattern to match: [text](url), `code`, ***bold italic***, **bold**, *italic*
    pattern = re.compile(r'(\[.+?\]\(.+?\)|`[^`]+`|\*\*\*.*?\*\*\*|___.*?___|\*\*.*?\*\*|__.*?__|\*.*?\*|_.*?_)')
    parts = pattern.split(text)
    result = []
    
    for part in parts:
        if not part:
            continue
            
        if part.startswith('[') and '](' in part and part.endswith(')'):
            close_bracket = part.find(']')
            link_text = part[1:close_bracket]
            url = part[close_bracket+2:-1]
            
            link_tag = f"link_{len(link_bindings)}"
            link_bindings.append((link_tag, url))
            
            result.append((link_text, tuple(base_tags) + ("link", link_tag)))
        elif part.startswith('`') and part.endswith('`'):
            result.append((part[1:-1], tuple(base_tags) + ("code",)))
        elif part.startswith('***') and part.endswith('***'):
            result.append((part[3:-3], tuple(base_tags) + ("bold_italic",)))
        elif part.startswith('___') and part.endswith('___'):
            result.append((part[3:-3], tuple(base_tags) + ("bold_italic",)))
        elif part.startswith('**') and part.endswith('**'):
            result.append((part[2:-2], tuple(base_tags) + ("bold",)))
        elif part.startswith('__') and part.endswith('__'):
            result.append((part[2:-2], tuple(base_tags) + ("bold",)))
        elif part.startswith('*') and part.endswith('*'):
            result.append((part[1:-1], tuple(base_tags) + ("italic",)))
        elif part.startswith('_') and part.endswith('_'):
            result.append((part[1:-1], tuple(base_tags) + ("italic",)))
        else:
            result.append((part, tuple(base_tags)))
            
    return result


def render_markdown(textbox, markdown_text):
    target = textbox._textbox if hasattr(textbox, "_textbox") else textbox
    
    is_dark = ctk.get_appearance_mode().lower() == "dark"
    h1_color = "#90CDF4" if is_dark else "#1A365D"
    h2_color = "#CBD5E0" if is_dark else "#2D3748"
    code_bg = "#2D3748" if is_dark else "#EDF2F7"
    code_fg = "#F7FAFC" if is_dark else "#2D3748"
    hr_color = "#4A5568" if is_dark else "#E2E8F0"
    quote_fg = "#A0AEC0" if is_dark else "#4A5568"
    link_fg = "#90CDF4" if is_dark else "#2B6CB0"
    
    # Configure tags on underlying tk.Text widget
    target.tag_config("h1", font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"), foreground=h1_color)
    target.tag_config("h2", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), foreground=h2_color)
    target.tag_config("h3", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), foreground=h2_color)
    target.tag_config("bold", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
    target.tag_config("italic", font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"))
    target.tag_config("bold_italic", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold", slant="italic"))
    target.tag_config("code", font=ctk.CTkFont(family="Consolas", size=10), background=code_bg, foreground=code_fg)
    target.tag_config("code_block", font=ctk.CTkFont(family="Consolas", size=10), background=code_bg, foreground=code_fg)
    target.tag_config("bullet", lmargin1=15, lmargin2=25)
    target.tag_config("bullet_marker", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), foreground=h1_color)
    target.tag_config("quote", font=ctk.CTkFont(family="Segoe UI", size=11, slant="italic"), foreground=quote_fg, lmargin1=20, lmargin2=20)
    target.tag_config("hr", font=ctk.CTkFont(family="Segoe UI", size=11), foreground=hr_color)
    target.tag_config("link", foreground=link_fg, underline=True)
    
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")
    
    lines = markdown_text.splitlines()
    in_code_block = False
    code_block_lines = []
    link_bindings = []
    
    for line in lines:
        if line.strip().startswith("```"):
            if in_code_block:
                content = "\n".join(code_block_lines) + "\n"
                target.insert("end", content, ("code_block",))
                in_code_block = False
                code_block_lines = []
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            code_block_lines.append(line)
            continue
            
        # Block quotes
        if line.startswith(">"):
            content = line[1:].lstrip()
            inline_parts = parse_inline(content, ("quote",), link_bindings)
            for text, tags in inline_parts:
                target.insert("end", text, tags)
            target.insert("end", "\n")
            continue
            
        # Headers
        header_match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2)
            tag = f"h{min(level, 3)}"
            
            inline_parts = parse_inline(content, (tag,), link_bindings)
            if target.index("insert") != "1.0":
                target.insert("end", "\n")
            for text, tags in inline_parts:
                target.insert("end", text, tags)
            target.insert("end", "\n\n")
            continue
            
        # Horizontal rules
        if line.strip() in ("---", "***", "___"):
            target.insert("end", "─" * 40 + "\n\n", ("hr",))
            continue
            
        # List items
        list_match = re.match(r'^(\s*)[-*+]\s+(.*)$', line)
        if list_match:
            content = list_match.group(2)
            target.insert("end", "  • ", ("bullet_marker",))
            inline_parts = parse_inline(content, ("bullet",), link_bindings)
            for text, tags in inline_parts:
                target.insert("end", text, tags)
            target.insert("end", "\n")
            continue
            
        # Normal line
        if line.strip() == "":
            target.insert("end", "\n")
        else:
            inline_parts = parse_inline(line, (), link_bindings)
            for text, tags in inline_parts:
                target.insert("end", text, tags)
            target.insert("end", "\n")
            
    # Link events bindings
    for tag_name, url in link_bindings:
        def make_handler(u):
            return lambda event: webbrowser.open_new_tab(u)
        
        def make_enter():
            return lambda event: target.config(cursor="hand2")
            
        def make_leave():
            return lambda event: target.config(cursor="arrow")
            
        target.tag_bind(tag_name, "<Button-1>", make_handler(url))
        target.tag_bind(tag_name, "<Enter>", make_enter())
        target.tag_bind(tag_name, "<Leave>", make_leave())
        
    textbox.configure(state="disabled")


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
            f"Se ha detectado la versión v{new_v} en GitHub. Tu versión actual es v{current_v}.\n"
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
        
        # Render markdown to textbox
        render_markdown(self.notes_text, notes_content)
        
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
