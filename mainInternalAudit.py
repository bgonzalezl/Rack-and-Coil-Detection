import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from PIL import Image, ImageTk
import os
from process_methods import *
from threading import Thread
import pandas as pd
import socket
import time

# Configuración de tema y apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
#C:\Games\python\Truper_2.MP4
#C:\Games\python\DJI_BEST.MP4

class InternalAuditApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Internal Audit System")
        self.root.geometry("1080x720")
        self.root.resizable(False, False)
        
        # Variables de configuración
        self.ip_asignada = tk.StringVar()
        self.tamano_filas = tk.StringVar(value="10")
        self.tamano_columnas = tk.StringVar(value="10")
        
        # Usuarios y contraseñas (en producción usar base de datos)
        self.usuarios = {
            "admin": {"password": "admin123", "role": "administrator"},
            "config": {"password": "config123", "role": "configuration"},
            "user": {"password": "user123", "role": "configuration"}
        }
        
        # Colores profesionales basados en el logo
        self.colors = {
            "primary": "#1e3d59",      # Azul oscuro profesional
            "secondary": "#2e5266",    # Azul medio
            "accent": "#00aaff",       # Azul claro tecnológico
            "background": "#0d1117",   # Fondo oscuro
            "surface": "#161b22",      # Superficie
            "text": "#ffffff",         # Texto blanco
            "text_secondary": "#8b949e" # Texto secundario
        }

        # Cola de detecciones (code, timestamp)
        self.detection_queue = []
        # Información de cada círculo de la pirámide
        self.pyramid_info = []
        
        self.setup_styles()
        self.create_login_screen()
        
    def setup_styles(self):
        """Configurar estilos personalizados"""
        # Configurar colores del tema
        ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = [self.colors["surface"], self.colors["surface"]]
        ctk.ThemeManager.theme["CTkButton"]["fg_color"] = [self.colors["primary"], self.colors["primary"]]
        ctk.ThemeManager.theme["CTkButton"]["hover_color"] = [self.colors["secondary"], self.colors["secondary"]]
        
    def clear_window(self):
        """Limpiar la ventana actual"""
        for widget in self.root.winfo_children():
            widget.destroy()
            
    def create_logo_frame(self, parent):
        """Crear frame con logo"""
        logo_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        try:
            # Cargar imagen del logo
            # Cambiar "logo.png" por la ruta de tu imagen
            logo_image = Image.open("logo.png")
            # Redimensionar la imagen (ajustar tamaño según necesites)
            logo_image = logo_image.resize((100, 100), Image.Resampling.LANCZOS)
            logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(100, 100))
            
            # Crear label con la imagen
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=logo_photo,
                text=""  # Sin texto para mostrar solo la imagen
            )
            logo_label.pack(pady=10)
            
        except FileNotFoundError:
            # Si no se encuentra la imagen, mostrar texto alternativo
            error_label = ctk.CTkLabel(
                logo_frame, 
                text="LOGO\nNO ENCONTRADO", 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["text_secondary"]
            )
            error_label.pack(pady=10)
            
        except Exception as e:
            # Manejo de otros errores al cargar la imagen
            error_label = ctk.CTkLabel(
                logo_frame, 
                text="ERROR\nCARGANDO LOGO", 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=self.colors["text_secondary"]
            )
            error_label.pack(pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            logo_frame, 
            text="INTERNAL AUDIT", 
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=self.colors["text"]
        )
        title_label.pack(pady=10)
        
        return logo_frame
        
    def create_login_screen(self):
        """Crear pantalla de login"""
        self.clear_window()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Logo
        logo_frame = self.create_logo_frame(main_frame)
        logo_frame.pack(pady=(30, 15))
        
        # Frame de login
        login_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"],
                                  corner_radius=15, border_width=2,
                                  border_color=self.colors["primary"])
        login_frame.pack(pady=25, padx=100, fill="x")
        
        # Título LOGIN
        login_title = ctk.CTkLabel(
            login_frame, 
            text="LOGIN", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors["text"]
        )
        login_title.pack(pady=(20, 10))
        
        # Campo Usuario
        usuario_label = ctk.CTkLabel(
            login_frame, 
            text="Usuario", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        usuario_label.pack(pady=(10, 5))
        
        self.usuario_entry = ctk.CTkEntry(
            login_frame,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.usuario_entry.pack(pady=(0, 10))
        
        # Campo Contraseña
        contrasena_label = ctk.CTkLabel(
            login_frame, 
            text="Contraseña", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        contrasena_label.pack(pady=(0, 5))
        
        self.contrasena_entry = ctk.CTkEntry(
            login_frame,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            show="*",
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.contrasena_entry.pack(pady=(0, 15))
        
        # Botón de login
        login_button = ctk.CTkButton(
            login_frame,
            text="INICIAR SESIÓN",
            width=300,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["primary"],
            command=self.authenticate_user
        )
        login_button.pack(pady=(10, 30))
        
        # Bind Enter key
        self.root.bind('<Return>', lambda event: self.authenticate_user())
        
    def authenticate_user(self):
        """Autenticar usuario"""
        username = self.usuario_entry.get().strip()
        password = self.contrasena_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor ingrese usuario y contraseña")
            return
            
        if username in self.usuarios and self.usuarios[username]["password"] == password:
            role = self.usuarios[username]["role"]
            if role == "administrator":
                self.create_administrator_screen()
            else:
                self.create_configuration_screen()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            
    def create_administrator_screen(self):
        """Crear pantalla de administrador"""
        self.clear_window()
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header con logo pequeño y título
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame, 
            text="ADMINISTRADOR", 
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["text"]
        )
        title_label.pack()
        
        # Frame de botones
        buttons_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"],
                                    corner_radius=15, border_width=2,
                                    border_color=self.colors["primary"])
        buttons_frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        # Botones de administrador
        buttons_data = [
            ("Creación de usuarios", self.crear_usuarios),
            ("Reporte de vuelta", self.reporte_vuelta),
            ("Editar de usuarios", self.editar_usuarios),
            ("Eliminar de usuarios", self.eliminar_usuarios)
        ]
        
        for i, (text, command) in enumerate(buttons_data):
            button = ctk.CTkButton(
                buttons_frame,
                text=text,
                width=400,
                height=60,
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color=self.colors["primary"],
                hover_color=self.colors["accent"],
                command=command,
                corner_radius=10
            )
            button.pack(pady=20, padx=50)
            
        # Botón de logout
        logout_button = ctk.CTkButton(
            main_frame,
            text="CERRAR SESIÓN",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors["secondary"],
            hover_color="#cc0000",
            command=self.create_login_screen
        )
        logout_button.pack(pady=20)

    
        
    def create_configuration_screen(self):
        """Crear pantalla de configuración"""
        self.clear_window()

        #Variables de configuración
        self.tipo_almacen = tk.StringVar(value="Seleccionar tipo de almacén")
        self.posicion = tk.StringVar()

        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 30))
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="CONFIGURACIÓN", 
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=self.colors["text"]
        )
        title_label.pack()
        
        # PARTE SUPERIOR  -  IP y Tipo de Almacén
        upper_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"],
                                   corner_radius=15, border_width=2,
                                   border_color=self.colors["primary"])
        upper_frame.pack(fill="x", padx=50, pady=(10, 10))

        #Subframe izquierdo
        left_frame = ctk.CTkFrame(upper_frame, fg_color="transparent")
        left_frame.pack(side="left", expand=True, fill="both", padx=(20,10), pady=10)
        
        # IP Asignada
        ip_label = ctk.CTkLabel(
            left_frame, 
            text="IP Asignada", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        ip_label.pack(pady=(10, 5))

        # Checkbox para alternar el texto del label de IP
        def toggle_ip_label():
            hostname = socket.gethostname()
            IPAddr = str(socket.gethostbyname(hostname))
            if ip_checkbox_var.get():
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, f"rtmp://{IPAddr}:1935/live")
            else:
                self.ip_entry.delete(0, tk.END)
                self.ip_entry.insert(0, "Ingrese la ruta del archivo")
        
        self.ip_asignada = tk.StringVar(value="Ingrese la ruta del archivo") # Valor por defecto
        self.ip_entry = ctk.CTkEntry(
            left_frame,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.ip_asignada,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.ip_entry.pack(pady=(0, 15))
        
        ip_checkbox_var = tk.BooleanVar(value=False)
        ip_checkbox = ctk.CTkCheckBox(
            left_frame,
            text="Alternar IP",
            variable=ip_checkbox_var,
            command=toggle_ip_label,
            checkbox_height=20,
            checkbox_width=20
        )
        ip_checkbox.pack(pady=(0, 5))

        # Tipo de Almacén
        tipo_label = ctk.CTkLabel(
            left_frame,
            text="Tipo de Almacén",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        tipo_label.pack(pady=(0, 5))

        self.tipo_combobox = ctk.CTkComboBox(
            left_frame,
            values=["Almacenes internos", "Rollos de acero"],
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.on_tipo_almacen_change,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"],
            button_color=self.colors["primary"],
            button_hover_color=self.colors["accent"]
        )
        self.tipo_combobox.pack(pady=(0, 20))

        # Subframe derecho
        right_frame = ctk.CTkFrame(upper_frame, fg_color="transparent")
        right_frame.pack(side="right", expand=True, fill="both", padx=(10, 20), pady=10)
        
        # Longitud de caracteres del ID
        id_length_label = ctk.CTkLabel(
            right_frame,
            text="Longitud de caracteres del ID",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        id_length_label.pack(pady=(10, 5))

        self.id_length = tk.StringVar(value="10") # Valor por defecto
        self.id_length_entry = ctk.CTkEntry(
            right_frame,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.id_length,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.id_length_entry.pack(pady=(0, 15))

        # Nombre de la ubicación
        ubicacion_label = ctk.CTkLabel(
            right_frame,
            text="Nombre de la ubicación",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        ubicacion_label.pack(pady=(5, 5))

        self.ubicacion_nombre = tk.StringVar(value="Introduzca la ubicación")
        ubicacion_entry = ctk.CTkEntry(
            right_frame,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.ubicacion_nombre,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        ubicacion_entry.pack(pady=(0, 10))

        self.save_video_var = tk.BooleanVar(value=False)
        video_checkbox = ctk.CTkCheckBox(
            right_frame,
            text="¿Guardar video al finalizar?",
            variable=self.save_video_var,
            checkbox_height=20,
            checkbox_width=20
        )
        video_checkbox.pack(pady=(0, 10))

        # PARTE INFERIOR  -  Posicíon y Dimensones
        self.lower_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"],
                                        corner_radius=15, border_width=2,
                                        border_color=self.colors["primary"])
        self.lower_frame.pack(expand=True, fill="x", padx=50, pady=(10, 0))

        # Posición
        posicion_label = ctk.CTkLabel(
            self.lower_frame,
            text="Posición",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        posicion_label.pack(pady=(20, 5))

        self.posicion_entry = ctk.CTkEntry(
            self.lower_frame,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.posicion,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.posicion_entry.pack(pady=(0, 20))

        #Frame para las dimensiones (se actualiza según tipo de almacén)
        self.dimensions_frame = ctk.CTkFrame(self.lower_frame, fg_color="transparent")
        self.dimensions_frame.pack(pady=(0, 10))

        #Mensaje inicial
        self.create_initial_message()

        # Botón Aceptar
        accept_button = ctk.CTkButton(
            self.lower_frame,
            text="Aceptar",
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=self.colors["accent"],
            hover_color=self.colors["primary"],
            command=self.apply_configuration
        )
        accept_button.pack(pady=(0, 10))
        
        # Botón de logout
        logout_button = ctk.CTkButton(
            main_frame,
            text="CERRAR SESIÓN",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors["secondary"],
            hover_color="#cc0000",
            command=self.create_login_screen
        )
        logout_button.pack(side="right", pady=(10, 15), padx=(0, 20))
    
    def create_initial_message(self):
        """Crear mensaje inicial cuando no se ha seleccionado tipo de almacén"""
        # Limpiar frame de dimensiones
        for widget in self.dimensions_frame.winfo_children():
            widget.destroy()
            
        message_label = ctk.CTkLabel(
            self.dimensions_frame, 
            text="Seleccione un tipo de almacén para continuar", 
            font=ctk.CTkFont(size=16),
            text_color=self.colors["text_secondary"]
        )
        message_label.pack(pady=20)
        
    def on_tipo_almacen_change(self, value):
        """Manejar cambio en el tipo de almacén"""
        self.tipo_almacen.set(value)

        # Limpiar frame de dimensiones
        for widget in self.dimensions_frame.winfo_children():
            widget.destroy()
            
        if value == "Almacenes internos":
            self.create_almacenes_internos_fields()
        elif value == "Rollos de acero":
            self.create_rollos_acero_fields()
            
    def create_almacenes_internos_fields(self):
        """Crear campos para Almacenes internos"""
        # Título
        titulo_label = ctk.CTkLabel(
            self.dimensions_frame, 
            text="Configuración de Almacenes Internos", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        titulo_label.pack(pady=(0, 5))
        
        # Frame para filas y columnas
        campos_frame = ctk.CTkFrame(self.dimensions_frame, fg_color="transparent")
        campos_frame.pack(pady=(0, 10))
        
        # Filas
        filas_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        filas_frame.pack(side="left", padx=20)
        
        filas_label = ctk.CTkLabel(
            filas_frame, 
            text="Filas", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        filas_label.pack()
        
        self.filas_entry = ctk.CTkEntry(
            filas_frame,
            width=100,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.tamano_filas,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.filas_entry.pack(pady=5)
        
        # X separator
        x_label = ctk.CTkLabel(
            campos_frame, 
            text="×", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        x_label.pack(side="left", padx=10)
        
        # Columnas
        columnas_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        columnas_frame.pack(side="left", padx=20)
        
        columnas_label = ctk.CTkLabel(
            columnas_frame, 
            text="Columnas", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        columnas_label.pack()
        
        self.columnas_entry = ctk.CTkEntry(
            columnas_frame,
            width=100,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.tamano_columnas,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.columnas_entry.pack(pady=5)
        
    def create_rollos_acero_fields(self):
        """Crear campos para Rollos de acero"""
        # Variables adicionales para rollos
        self.rollos_base = tk.StringVar(value="10")
        self.apilamientos = tk.StringVar(value="5")
        
        # Título
        titulo_label = ctk.CTkLabel(
            self.dimensions_frame, 
            text="Configuración de Rollos de Acero", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text"]
        )
        titulo_label.pack(pady=(0, 5))
        
        # Frame para rollos en base y apilamientos
        campos_frame = ctk.CTkFrame(self.dimensions_frame, fg_color="transparent")
        campos_frame.pack(pady=(0, 10))
        
        # Rollos en base
        base_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        base_frame.pack(side="left", padx=20)
        
        base_label = ctk.CTkLabel(
            base_frame, 
            text="Rollos en base", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        base_label.pack()
        
        self.base_entry = ctk.CTkEntry(
            base_frame,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.rollos_base,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.base_entry.pack(pady=5)
        
        # X separator
        x_label = ctk.CTkLabel(
            campos_frame, 
            text="×", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors["text"]
        )
        x_label.pack(side="left", padx=10)
        
        # Apilamientos
        apilamientos_frame = ctk.CTkFrame(campos_frame, fg_color="transparent")
        apilamientos_frame.pack(side="left", padx=20)
        
        apilamientos_label = ctk.CTkLabel(
            apilamientos_frame, 
            text="Apilamientos", 
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text_secondary"]
        )
        apilamientos_label.pack()
        
        self.apilamientos_entry = ctk.CTkEntry(
            apilamientos_frame,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            textvariable=self.apilamientos,
            border_color=self.colors["primary"],
            fg_color=self.colors["background"]
        )
        self.apilamientos_entry.pack(pady=5)

    def apply_configuration(self):
        ip = self.ip_asignada.get().strip()
        posicion = self.posicion.get().strip()
        tipo = self.tipo_combobox.get()
        #
        save_video = self.save_video_var.get()
        ubicacion = self.ubicacion_nombre.get().strip()


        if tipo == "Almacenes internos":
            filas = self.tamano_filas.get().strip()
            columnas = self.tamano_columnas.get().strip()
            id_length = self.id_length.get().strip() 

            if not ip or not posicion or not filas or not columnas or not id_length or not ubicacion:
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return

            try:
                filas_int = int(filas)
                columnas_int = int(columnas)
                id_length_int = int(id_length)
                if filas_int <= 0 or columnas_int <= 0 or int(id_length_int) <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Filas, columnas e ID deben ser enteros positivos")
                return

            # Mostrar confirmación y abrir pantalla
            messagebox.showinfo("Configuración", f"Configuración aplicada:\nIP: {ip}\nRack: {filas}×{columnas}\nID Length: {id_length}\nUbicación: {ubicacion}\nGuardado de video: {save_video}")
            self.create_work_screen(ip, posicion, tipo, filas_int, columnas_int, id_length_int, ubicacion, save_video)

        elif tipo == "Rollos de acero":
            base = self.rollos_base.get().strip()
            apilamientos = self.apilamientos.get().strip()
            id_length = self.id_length.get().strip()

            if not ip or not posicion or not base or not apilamientos or not id_length or not ubicacion:
                messagebox.showerror("Error", "Por favor complete todos los campos")
                return

            try:
                base_int = int(base)
                apilamientos_int = int(apilamientos)
                id_length_int = int(id_length)
                if base_int <= 0 or apilamientos_int <= 0 or id_length_int <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Base, apilamientos e ID deben ser enteros positivos")
                return

            messagebox.showinfo("Configuración", f"Configuración aplicada:\nIP: {ip}\nAcomodo: {base}×{apilamientos}\nID Length: {id_length}\nUbicación: {ubicacion}\nGuardado de video: {save_video}")
            self.create_work_screen(ip, posicion, tipo, base_int, apilamientos_int, id_length_int, ubicacion, save_video)

    def draw_pyramid(self, parent, base, height):
        # Limpiar contenido anterior
        for widget in parent.winfo_children():
            widget.destroy()

        # Crear canvas expandible
        canvas = tk.Canvas(parent, bg=self.colors["surface"], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        self.pyramid_canvas = canvas
        self.pyramid_items = []
        self.current_circle_index = 0

        # Inicializamos pyramid_info con todos los IDs, del mayor al menor
        self.pyramid_info = [
            {"ID_circulo": idx, "color": None, "codigo": None, "timestamp": None}
            for idx in range(base * height, 0, -1)
        ]

        def draw():
            canvas.delete("all")  # Limpiar canvas
            self.pyramid_items.clear()
            roll_number = 1
            

            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Cálculo de tamaño de botón adaptado
            max_button_diameter_x = canvas_width // (base + 2)
            max_button_diameter_y = canvas_height // (height + 2)
            button_diameter = min(max_button_diameter_x, max_button_diameter_y, 40)
            button_radius = button_diameter // 2
            spacing_x = button_radius // 2
            spacing_y = button_radius

            total_pyramid_height = height * (button_diameter + spacing_y) - spacing_y
            start_y = (canvas_height - total_pyramid_height) // 2  # Centrado vertical

            for level in reversed(range(height)):
                rolls_in_level = base - level
                total_row_width = rolls_in_level * button_diameter + (rolls_in_level - 1) * spacing_x
                start_x = (canvas_width - total_row_width) // 2  # Centrado horizontal
                y = start_y + (height - level - 1) * (button_diameter + spacing_y)

                for i in range(rolls_in_level):
                    x = start_x + i * (button_diameter + spacing_x)
                    ov = canvas.create_oval(x, y, x + button_diameter, y + button_diameter, fill="black")
                    canvas.create_text(x + button_radius, y + button_radius, text=str(roll_number), fill="white")
                    self.pyramid_items.append(ov)
                    roll_number += 1
            
            if self.pyramid_items:
                # primer círculo a pintar: último de la lista
                self.current_circle_index = len(self.pyramid_items) - 1
                canvas.itemconfig(self.pyramid_items[self.current_circle_index], fill="yellow")

        # Redibujar al cambiar tamaño del canvas
        canvas.bind("<Configure>", lambda event: draw())

    def create_work_screen(self, ip, posicion, tipo_almacen, dim1, dim2, id_length, ubicacion, save_video):
        """Crear pantalla de trabajo con la configuración aplicada"""
        self.cap = None #Input de video
        self.is_program_activated = False
        self.true_width, self.true_height = 0, 0
        self.rack_counter = 0
        self.current_state = 0
        self.height_frame, self.width_frame = 0, 0
        self.last_codebar_found = "None"
        self.info_tuple = []
        self.frame_count = 0
        self.prev_detections = []
        self.saved_codebars = pd.DataFrame()
        self.out = None
        # Cargar la imagen de la marca de agua
        self.watermark = cv2.imread('C:/Games/python/logo.png', cv2.IMREAD_UNCHANGED)


        def inicio_vuelo():
            self.is_program_activated = True
            iniciar_vuelo.configure(state="disabled")
            btn_exportar.configure(state="disabled")
            self.btn_blue.configure(state="normal")
            self.btn_red.configure(state="normal")

            def flight_start():
                if(self.is_program_activated):
                    time.sleep(3)
                    self.cap = cv2.VideoCapture(ip)
                    self.height_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.width_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                    #self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    self.fourcc = 1
                    output_folder="Backup"
                    if save_video:
                        self.video_route = os.path.join(output_folder, f"Detecciones_{ubicacion}_{posicion}_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.mp4")
                        #self.video_route = f"Backup\Detecciones_{ubicacion + posicion + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.mp4"
                        self.out = cv2.VideoWriter(self.video_route, self.fourcc, self.fps, (self.width_frame, self.height_frame))
                    print(int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                    print(int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
                    if not self.cap.isOpened():
                        print("Error al abrir la fuente de video.")
                        return
                    
                    if self.true_height == 0 and self.true_width == 0:
                        self.true_width = self.og_video.winfo_width()
                        self.true_height = self.og_video.winfo_height()
                                
                    self.root.after(100, actualizar_video)
                else:
                    print("Fin del video o error.")
                    finalizar_vuelo()
                    return
            
            t1 = Thread(target=flight_start, daemon=False)
            t1.start()
            return
        
        def actualizar_video():
            if not self.is_program_activated or not self.cap:
                return

            ret, frame = self.cap.read()
            if not ret:
                print("Fin del video o error.")
                finalizar_vuelo()
                return
            
            # Video original
            new_height = int(self.height_frame/2)
            new_width = int(self.width_frame/2)
            chopped_array = cv2.resize(frame, (new_width,new_height))
            frame_rgb = cv2.cvtColor(chopped_array, cv2.COLOR_BGR2RGBA)
            img_rgb = Image.fromarray(frame_rgb)
            img_rgb_ctk = ctk.CTkImage(light_image=img_rgb, size=(self.true_width, self.true_height))
            self.og_video.configure(image=img_rgb_ctk)
            self.og_video.image = img_rgb_ctk

            # Procesamiento cada 15 frames
            def proceso_actualizacion(frame):
                # Nuevos métodos para pintar y habilitar botones
                

                if self.frame_count % 10 == 0:
                    match tipo_almacen:
                        case "Almacenes internos":
                            processed_frame, self.rack_counter, self.current_state = rack_preprocessing(frame, self.rack_counter, self.current_state)
                        case "Rollos de acero":
                            found_codes, processed_frame, current_roi = coil_processing(frame, self.rack_counter, id_length, self.prev_detections, self.frame_count)
                            print(found_codes)
                            self.saved_codebars, was_updated = dataframe_update(found_codes, self.saved_codebars, current_roi)
                            if was_updated:
                                idx = self.current_circle_index
                                if idx > len(self.pyramid_items) - 1:
                                    idx = len(self.pyramid_items) - 1
                                print(f"A pintar {self.pyramid_items[idx]}")
                                # Repintamos el círculo
                                self.pyramid_canvas.itemconfig(self.pyramid_items[idx], fill="green")

                                # Avanzar al anterior
                                self.current_circle_index -= 1
                                if self.current_circle_index >= 0:
                                    self.pyramid_canvas.itemconfig(
                                    self.pyramid_items[self.current_circle_index], fill="yellow"
                                    )
                                else:
                                    # fin del recorrido
                                    for btn in (self.btn_blue, self.btn_red):
                                        btn.configure(state="disabled")

                        #C:\Games\python\DJI_BEST.MP4
                        case "PANEL":
                            #to do
                            processed_frame = frame
                else:   
                    processed_frame = frame
                final_color = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGBA)
                processed_img_rgb = Image.fromarray(final_color)
                processed_img_rgb_ctk = ctk.CTkImage(light_image=processed_img_rgb, size=(self.true_width, self.true_height))
                self.process_video.configure(image=processed_img_rgb_ctk)
                self.process_video.image = processed_img_rgb_ctk
                if save_video:
                    to_save = watermarker(frame, self.watermark, self.width_frame, self.height_frame)
                    self.out.write(to_save)

            proceso_actualizacion(frame)
            self.frame_count+=1
            self.root.after(16, actualizar_video)


        def finalizar_vuelo():
            iniciar_vuelo.configure(state="normal")
            btn_exportar.configure(state="normal")
            self.btn_blue.configure(state="disabled")
            self.btn_red.configure(state="disabled")
            self.is_program_activated = False
            self.frame_count = 0
            if self.cap:
                self.cap.release()
                self.cap = None

        def exportar():
            csv_path, json_path = json_csv_export(self.saved_codebars, ubicacion, posicion)
            if self.out and save_video:
                self.out.release()
                self.out = None
                messagebox.showinfo("Exportación", f"Archivos exportados a: \n{csv_path}\n{json_path}\n{self.video_route}")
                print(f"Archivos exportados a: \n{csv_path}\n{json_path}\n{self.video_route}")
                self.saved_codebars.iloc[0:0]
            else:
                messagebox.showinfo("Exportación", f"Archivos exportados a: \n {csv_path} \n {json_path}")
                print(f"Archivos exportados a: \n {csv_path} \n {json_path}")
                self.saved_codebars.iloc[0:0]
            #self.saved_codebars=pd.DataFrame(data=None, columns=self.saved_codebars.columns)

        def paint_circle(color):
            idx = self.current_circle_index
            found_codes = []
            if idx is None or idx < 0:
                return

            # Si es verde, tomamos el siguiente código de la cola
            #codigo, ts = None, None
            if color == "green":
                print("Rollo añadido")
            else:
                if color == "blue":
                    found_codes.append({"type": "ID", "value": 'Sin Rollo'})
                    #found_codes = [{'type': 'ID', 'value': 'Sin Rollo'}]#["Sin Rollo"]
                    current_roi = []
                else:
                    #found_codes = [{'type': 'ID', 'value': 'Etiqueta no encontrada'}]#["Etiqueta no encontrada"]
                    found_codes.append({"type": "ID", "value": 'Etiqueta no encontrada'})
                    current_roi = []

                self.saved_codebars, was_updated = dataframe_update(found_codes, self.saved_codebars, current_roi)

            # Repintamos el círculo
            self.pyramid_canvas.itemconfig(self.pyramid_items[idx], fill=color)

            # Avanzar al anterior
            self.current_circle_index -= 1
            if self.current_circle_index >= 0:
                self.pyramid_canvas.itemconfig(
                    self.pyramid_items[self.current_circle_index], fill="yellow"
                )
            else:
                # fin del recorrido
                for btn in (self.btn_blue, self.btn_red):
                    btn.configure(state="disabled")
        

        self.clear_window()
    
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Frame de botones con layout grid
        buttons_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"],
                                 corner_radius=15, border_width=2,
                                 border_color=self.colors["primary"])
        buttons_frame.pack(fill="x", pady=20, padx=50)
        buttons_frame.grid_columnconfigure((0,1,2,3), weight=1)

        # Label de tiempo a la izquierda
        self.flight_time_label = ctk.CTkLabel(
            buttons_frame,
            text="Tiempo de vuelo: 00:00",
            font=ctk.CTkFont(size=14),
            text_color=self.colors["text"],
            anchor="w"
        )
        self.flight_time_label.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        iniciar_vuelo = ctk.CTkButton(
                buttons_frame,
                text="Iniciar vuelo",
                width=200,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors["primary"],
                hover_color=self.colors["accent"],
                command=inicio_vuelo,
                corner_radius=10
            )
        
        detener_vuelo = ctk.CTkButton(
                buttons_frame,
                text="Detener vuelo",
                width=200,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors["primary"],
                hover_color=self.colors["accent"],
                command=finalizar_vuelo,
                corner_radius=10
            )

        btn_exportar = ctk.CTkButton(
                buttons_frame,
                text="Exportar",
                width=200,
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color=self.colors["primary"],
                hover_color=self.colors["accent"],
                command=exportar,
                corner_radius=10
            )

        iniciar_vuelo.grid(row=0, column=1, padx=10, pady=10)
        detener_vuelo.grid(row=0, column=2, padx=10, pady=10)
        btn_exportar.grid(row=0, column=3, padx=10, pady=10)

        # Frame de botones con layout grid
        process_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["surface"],
                                 corner_radius=15, border_width=2,
                                 border_color=self.colors["primary"])
        process_frame.pack(fill="x", pady=20, padx=50)

        process_frame.pack(fill="both", expand=True, padx=50, pady=20)
        process_frame.grid_columnconfigure((0, 1), weight=1)
        process_frame.grid_rowconfigure((0, 1), weight=1)

        # Video original (arriba izquierda)
        self.og_video = ctk.CTkLabel(process_frame, text="", fg_color="black")
        self.og_video.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Video procesado (abajo izquierda)
        self.process_video = ctk.CTkLabel(process_frame, text="", fg_color="black")
        self.process_video.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Frame lateral para visualización tipo rack
        grid_frame = ctk.CTkFrame(
            process_frame, 
            fg_color=self.colors["surface"], 
            corner_radius=10,
            border_width=2,
            border_color=self.colors["primary"]
        )
        grid_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1)
        grid_frame.grid_rowconfigure(1, weight=1)

        # Sub-frame para representar la pirámide de rollos/racks
        self.rack_grid = ctk.CTkFrame(grid_frame, fg_color="white")
        self.rack_grid.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)
        self.rack_grid.grid_propagate(False) 

        # Lógica para generar grilla según tipo
        if tipo_almacen == "Almacenes internos":
            self.draw_pyramid(self.rack_grid,dim1, dim2)
        elif tipo_almacen == "Rollos de acero":
            self.draw_pyramid(self.rack_grid,dim1, dim2)

        # Botón de regreso
        back_button = ctk.CTkButton(
            main_frame,
            text="REGRESAR A CONFIGURACIÓN",
            width=250,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=self.colors["primary"],
            command=self.create_configuration_screen
        )
        back_button.pack(pady=20)

        # Botones de color, deshabilitados
        #self.btn_green = ctk.CTkButton(main_frame, text="Botón 1",
        #                               width=100, height=30,
        #                               fg_color="green",
        #                               state="disabled",
        #                               command=lambda: _paint_circle("green"))
        self.btn_blue  = ctk.CTkButton(main_frame, text="Botón 2",
                                       width=100, height=30,
                                       fg_color="blue",
                                       state="disabled",
                                       command=lambda: paint_circle("blue"))
        self.btn_red   = ctk.CTkButton(main_frame, text="Botón 3",
                                       width=100, height=30,
                                       fg_color="red",
                                       state="disabled",
                                       command=lambda: paint_circle("red"))

        self.btn_red.pack(side="right", padx=10, pady=5)
        self.btn_blue.pack(side="right", padx=10, pady=5)
        #self.btn_green.pack(side="right", padx=10, pady=5)

        
    # Métodos para funciones de administrador
    def crear_usuarios(self):
        messagebox.showinfo("Función", "Funcionalidad: Creación de usuarios")
        
    def reporte_vuelta(self):
        messagebox.showinfo("Función", "Funcionalidad: Reporte de vuelta")
        
    def editar_usuarios(self):
        messagebox.showinfo("Función", "Funcionalidad: Editar usuarios")
        
    def eliminar_usuarios(self):
        messagebox.showinfo("Función", "Funcionalidad: Eliminar usuarios")
        
    def run(self):
        """Ejecutar la aplicación"""
        self.root.mainloop()
        

# Crear y ejecutar la aplicación
if __name__ == "__main__":
    app = InternalAuditApp()
    app.run()