"""
Program Name: Secure Share Model
Author: Impresión 3D Móstoles
Social Media: https://mtr.bio/i3dm
Email: impresion3dmostoles@gmail.com
Date: 01/02/2025
Version: 0.20
License: AGPL v3

*** TIPs ***
Entorno:
    conda create --name SecureShareModel python=3.11
    conda activate SecureShareModel

Dependencias:
    Linux:
        conda install pillow
    Windows:
        conda install pillow
        
Compilar:
    conda install pyinstaller
    Linux:
        pyinstaller --onefile --windowed --clean --strip --optimize "2" --exclude-module=numpy --hidden-import PIL._tkinter_finder --add-data "SSMLogo.png:." SecureShareModelViewer.py
    Windows:
        pyinstaller --onefile  --windowed --clean --optimize "2" --exclude-module=numpy  --add-data "SSMLogo.png;." --icon SSMLogo.png  SecureShareModelViewer.py
        Reducido: pyinstaller SecureShareModelViewer.spec
"""

import os
from PIL import Image, ImageTk
import pickle
import tkinter as tk
from tkinter import filedialog, Canvas, Menu, Toplevel, PhotoImage
import tkinter.font as tkFont
import sys
import base64
import lzma

def remove_folder(folder_name):
    for root, dirs, files in os.walk(folder_name, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(folder_name)

class SecureShareModelViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.folder_name = None
        self.x, self.y, self.z = 0, 0, 0
        self.zoom_factor = 1.0
        self.logo_path = None
        self.events= False
        self.init_ui()

    def init_ui(self):
        self.title("Secure Share Model - #I3DM")
        self.canvas = Canvas(self, width=1200, height=800)
        self.canvas.pack()
        self.resizable(False, False)

        #Carga específica para ejecución desde fuentes o compilado.
        if getattr(sys, 'frozen', False):
            self.logo_path = os.path.join(sys._MEIPASS, "SSMLogo.png")
        else:
            self.logo_path = "SSMLogo.png"
        icon_image = PhotoImage(file=self.logo_path)
        self.iconphoto(True, icon_image)

        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Cargar SSM", command=self.load_images)
        file_menu.add_separator()
        file_menu.add_command(label="Cerrar", command=self.quit_viewer)
        self.menu_bar.add_cascade(label="Archivo", menu=file_menu)
        self.menu_bar.add_command(label="Ayuda", command=self.show_help)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        #Captura de eventos para movimiento con teclas en ventana TK
        self.bind("<Left>", lambda event: self.change_image("left"))
        self.bind("<Right>", lambda event: self.change_image("right"))
        self.bind("<Up>", lambda event: self.change_image("up"))
        self.bind("<Down>", lambda event: self.change_image("down"))
        self.bind("<w>", lambda event: self.change_image("w"))
        self.bind("<s>", lambda event: self.change_image("s"))
        self.bind("<Escape>", lambda event: self.quit_viewer())

        self.bind("<MouseWheel>", lambda event: self.zoom_image(1 if event.delta > 0 else -1))  # Windows y macOS
        self.bind("<Button-4>", lambda event: self.zoom_image( 1))
        self.bind("<Button-5>", lambda event: self.zoom_image( -1))

    def show_help(self):
        help_window = Toplevel(self)
        help_window.title("Secure Share Model - #I3DM")
        help_window.geometry("690x280")
        help_window.resizable(False, False)
        
        help_window.bind('<Escape>', lambda event: help_window.destroy())

        # Columna de la izquierda: Cargar la imagen
        image = Image.open(self.logo_path)
        logo_photo = ImageTk.PhotoImage(image)
        logo_label = tk.Label(help_window, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.grid(row=0, column=0, padx=10, pady=10, sticky="nw")
        
        # Columna de la derecha: Instrucciones sobre el funcionamiento
        help_text = """- Los cursores y 'W/S' rotan la pieza en los ejes XYZ.\n
- La rueda del ratón hace zoom.\n
- [Esc] cierra la aplicación.\n\n\n\n
Autor: Impresión 3D Móstoles\n
Contacto: impresion3dmostoles@gmail.com\n
Web: https://mtr.bio/i3dm"""
        _font = tkFont.Font(family="Console", size=10, weight=tkFont.BOLD)
        help_label = tk.Label(help_window, text=help_text, justify="left", font=_font, padx=10, pady=10)
        help_label.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

    #Diálogo para la selección de .ssm y extracción de imágenes.,Carga la imagen con coordenadas 0.0.0
    def load_images(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo ssm", filetypes=[("Share Model", "*.ssm")])
        self.geometry("1200x800")
        if file_path:
            self.zoom_factor=1 #reset zoom en inicio
            self.events=True
            self.extract_images(file_path)
            self.load_image()
    
    #Extraer las imágenes en un directorio temporal
    def extract_images(self, ssm_file):
        self.folder_name = os.path.join(os.path.dirname(ssm_file), os.path.splitext(os.path.basename(ssm_file))[0])
        os.makedirs(self.folder_name, exist_ok=True)

        with lzma.open(ssm_file, 'rb') as f:
            images_data = pickle.load(f)
        for image_name, image_data in images_data[0:]:
            image_path = os.path.join(self.folder_name, image_name)
            with open(image_path, 'wb') as img_file:
                img_file.write(base64.b64decode(image_data))

    #Generar el nombre de la imagen necesaria para las coordenadas actuales
    def get_image_filename(self):
        return os.path.join(self.folder_name, f"tmpModel_{self.x:03d}{self.y:03d}{self.z:03d}.png")

    #Carga de la imagen actual
    def load_image(self):
        filename = self.get_image_filename()
        try:
            image = Image.open(filename)
            image = image.resize((int(1200 * self.zoom_factor), int(800 * self.zoom_factor)), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            img_width, img_height = image.size

            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            x_pos = (canvas_width - img_width) // 2
            y_pos = (canvas_height - img_height) // 2

            self.canvas.create_image(x_pos, y_pos, anchor="nw", image=self.photo)
            self.title(f"Secure Share Model - #I3DM - Coordenadas: X:{self.x} / Y:{self.y} / Z:{self.z}")
        except Exception as e:
            print(f"No se pudo cargar la imagen: {filename}, error: {e}")
    
    #Cambia las coordenadas según en respuesta al evento de captura de teclas
    def change_image(self, direction):
        if(self.events):
            if direction == "left":
                self.y = (self.y + 45) % 360
            elif direction == "right":
                self.y = (self.y - 45) % 360
            elif direction == "up":
                self.x = (self.x - 45) % 360
            elif direction == "down":
                self.x = (self.x + 45) % 360
            elif direction == "w":
                self.z = (self.z + 45) % 360
            elif direction == "s":
                self.z = (self.z - 45) % 360
            self.load_image()

    # Cierra la ventana y elimina el directorio temporal
    def quit_viewer(self):
        if self.folder_name:
            remove_folder(self.folder_name)
        self.destroy()

    def on_close(self):
        print("La ventana está cerrándose.")
        self.quit_viewer()
        self.destroy()

    # Función para manejar el zoom con la rueda del ratón
    def zoom_image(self, direction):
        if(self.events):
            self.zoom_factor = max(1, self.zoom_factor + 0.1 * direction)
            self.load_image()

if __name__ == "__main__":
    app = SecureShareModelViewer()
    app.mainloop()
