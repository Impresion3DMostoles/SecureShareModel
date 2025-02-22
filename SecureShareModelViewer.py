"""
Program Name: Secure Share Model
Description: Este programa permite distribuir de forma segura modelos 3D a clientes. 
             Lee un archivo STL y genera un archivo SSM con imágenes estáticas, 
             simulando un rotado del modelo en dos ejes, sin incluir información 3D. 
Author: Impresión 3D Móstoles
WEB Page: https://mtr.bio/i3dm
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
        #pyinstaller --onefile --windowed --clean --strip --optimize "2" --exclude-module=numpy --hidden-import PIL._tkinter_finder --add-data "SSMLogo.png:." SecureShareModelViewer.py
    Windows:
        pyinstaller --onefile  --windowed --clean --optimize "2" --exclude-module=numpy  --add-data "SSMLogo.png;." SecureShareModelViewer.py
"""
#TO-DO: 
# No agrandar ventana si finalmente no se selecciona un SSM
# Hacer zoom en el visualizador
# Revisar texto de ayuda
# Agregar icono al ejecutable

import os
from PIL import Image,ImageTk
import pickle
import tkinter as tk
from tkinter import filedialog, Canvas, Menu, Toplevel,PhotoImage
import sys

#Eliminar directorio temporal después de usar
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
        self.logo_path = None
        self.init_ui()

    def init_ui(self):
        self.title("Secure Share Model - #I3DM")
        self.geometry("500x500")
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

        self.canvas = Canvas(self, width=1200, height=800)
        self.canvas.pack()

        #Captura de eventos para movimiento con teclas en ventana TK
        self.bind("<Left>", lambda event: self.change_image("left"))
        self.bind("<Right>", lambda event: self.change_image("right"))
        self.bind("<Up>", lambda event: self.change_image("up"))
        self.bind("<Down>", lambda event: self.change_image("down"))
        self.bind("<w>", lambda event: self.change_image("w"))
        self.bind("<s>", lambda event: self.change_image("s"))
        self.bind("<Escape>", lambda event: self.quit_viewer())


        text = """Gestor de ficheros \nSecure Share Model. \n\nGenera el fichero seleccionando un .stl de entrada\n\nCarga el modelo y usa los cursores para rotar la pieza\n[Esc para salir]"""

        label = tk.Label(self, text=text, wraplength=380, justify="center", bd=2, relief="solid", font=("Times New Roman", 18, "bold"))
        label.pack(pady=20, padx=10)

    def show_help(self):
        help_window = Toplevel(self)
        help_window.title("Secure Share Model - #I3DM")
        help_window.geometry("500x300")
        
        help_window.bind('<Escape>', lambda event: help_window.destroy())

        image = Image.open(self.logo_path)
        logo_photo = ImageTk.PhotoImage(image)
        logo_label = tk.Label(help_window, image=logo_photo)
        logo_label.image = logo_photo
        logo_label.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        
        help_text = """- Cargar SSM: Abre un archivo SSM.\n- Usa las flechas y W/S\n para rotar la imagen.\n- Pulsa Esc para salir."""
        help_label = tk.Label(help_window, text=help_text, justify="left", padx=10, pady=10)
        help_label.grid(row=1, column=1, padx=10, pady=10, sticky="nw")

        help_window.grid_rowconfigure(0, weight=1)
        help_window.grid_columnconfigure(0, weight=1)
        help_window.grid_columnconfigure(1, weight=3)

    #Diálogo para la selección de .ssm y extracción de imágenes.,Carga la imagen con coordenadas 0.0.0
    def load_images(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo ssm", filetypes=[("Share Model", "*.ssm")])
        self.geometry("1200x800")
        if file_path:
            self.extract_images(file_path)
            self.load_image()
    
    #Extraer las imágenes en un directorio temporal
    def extract_images(self, ssm_file):
        self.folder_name = os.path.join(os.path.dirname(ssm_file), os.path.splitext(os.path.basename(ssm_file))[0])
        os.makedirs(self.folder_name, exist_ok=True)

        with open(ssm_file, 'rb') as f:
            images_data = pickle.load(f)
        for image_name, image_data in images_data[0:]:
            image_path = os.path.join(self.folder_name, image_name)
            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)

    #Generar el nombre de la imagen necesaria para las coordenadas actuales
    def get_image_filename(self):
        return os.path.join(self.folder_name, f"tmpModel_{self.x:03d}{self.y:03d}{self.z:03d}.png")

    #Carga de la imagen actual
    def load_image(self):
        filename = self.get_image_filename()
        try:
            image = Image.open(filename)
            image = image.resize((1200, 800), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            self.title(f"Secure Share Model - #I3DM - Coordenadas: X:{self.x} / Y:{self.y} / Z:{self.z}")
        except Exception as e:
            print(f"No se pudo cargar la imagen: {filename}, error: {e}")
    
    #Cambia las coordenadas según en respuesta al evento de captura de teclas
    def change_image(self, direction):
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

    #Cierra la ventana y elimina el directorio temporal
    def quit_viewer(self):
        if self.folder_name:
            remove_folder(self.folder_name)
        self.destroy()

if __name__ == "__main__":
    app = SecureShareModelViewer()
    app.mainloop()