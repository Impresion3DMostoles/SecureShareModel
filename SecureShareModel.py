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
        conda install pillow numpy nomkl open3d=0.19.0
    Windows:
        conda install pillow numpy open3d=0.19.0
Compilar:
    conda install pyinstaller
    Linux:
        pyinstaller --noconfirm --onefile --windowed --clean --optimize "2" --strip --add-data "SSMLogo.png:."  SecureShareModel.py
    Windows:
        Default: pyinstaller --noconfirm --onefile --windowed --clean --optimize "2" --add-data "SSMLogo.png;."  SecureShareModel.py
        Reducido: pyinstaller SecureShareModel.spec
"""
#TO-DO: 
# No agrandar ventana si finalmente no se selecciona un SSM
# Hacer zoom en el visualizador
# Revisar texto de ayuda
# Agregar icono al ejecutable

import os
import sys
from PIL import Image,ImageTk
import pickle
import tkinter as tk
from tkinter import filedialog, Canvas, Menu, Toplevel,PhotoImage
import open3d as o3d
import math

#Eliminar directorio temporal después de usar
def remove_folder(folder_name):
    for root, dirs, files in os.walk(folder_name, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(folder_name)

#Diálogo selección fichero STL
def select_stl_file():
        file_path = filedialog.askopenfilename(title="Seleccionar archivo STL", filetypes=[("STL Files", "*.stl")])
        if file_path:
            return load_stl(file_path)

#Carga de modelo y conversión a mesh        
def load_stl(stl_path):
    try:
        stl_model = o3d.io.read_triangle_mesh(stl_path)
        if stl_model.is_empty(): return None, None
        folder_name = os.path.splitext(os.path.basename(stl_path))[0]
        os.makedirs(folder_name, exist_ok=True)
        return stl_model, folder_name
    except:
        return None, None

#Empaquetar imagenes en fichero .ssm
def save_images_to_ssm(folder_name):    
    images_data = []
    
    for image_file in os.listdir(folder_name):
        if image_file.endswith(f".png"):
            file_path = os.path.join(folder_name, image_file)
            with open(file_path, 'rb') as img_file:
                image_data = img_file.read()
            images_data.append((image_file, image_data))

    ssm_file = f"{os.path.splitext(os.path.basename(folder_name))[0]}.ssm"
    with open(ssm_file, 'wb') as f:
        pickle.dump(images_data, f)

    remove_folder(folder_name)

#Método pricipal de generación .ssm
def generate():
    stl_model, path = select_stl_file()

    os.makedirs(path, exist_ok=True)

    stl_model.compute_vertex_normals()
    stl_model.paint_uniform_color([0, 1, 0])

    vertices = list(stl_model.vertices)
    
    # Calcular el centroide (promedio de las coordenadas)
    centroid = [sum(coord) / len(coord) for coord in zip(*vertices)]

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="Generando SSM ", width=1200, height=800, left=200, top=600)
    vis.add_geometry(stl_model)

    vis.get_render_option().background_color = [0, 0, 1]
    vis.get_view_control().set_zoom(1) 

    for k in range(8):  # Rotación en Z (cada 45°)
        stl_model.translate([-centroid[0], -centroid[1], -centroid[2]])
        R_z = stl_model.get_rotation_matrix_from_xyz((0, 0, math.radians(45)))
        stl_model.rotate(R_z, center=(0, 0, 0))
        stl_model.translate([centroid[0], centroid[1], centroid[2]])

        for j in range(8):  # Rotación en Y (cada 45°)
            stl_model.translate([-centroid[0], -centroid[1], -centroid[2]])
            R_y = stl_model.get_rotation_matrix_from_xyz((0, math.radians(45), 0))
            stl_model.rotate(R_y, center=(0, 0, 0))
            stl_model.translate([centroid[0], centroid[1], centroid[2]])

            for i in range(8):  # Rotación en X (cada 45°)
                stl_model.translate([-centroid[0], -centroid[1], -centroid[2]])
                R_x = stl_model.get_rotation_matrix_from_xyz((math.radians(45), 0, 0))
                stl_model.rotate(R_x, center=(0, 0, 0))
                stl_model.translate([centroid[0], centroid[1], centroid[2]])

                #print(f"Rotación actual -> Z: {k*45}°, Y: {j*45}°, X: {i*45}°")

                # Redibujar escena
                vis.update_geometry(stl_model)
                vis.poll_events()
                vis.update_renderer()

                # Capturar imagen
                image_path = f"{path}/tmpModel_{k*45:03d}{j*45:03d}{i*45:03d}.png"
                vis.capture_screen_image(image_path)

    vis.destroy_window()

    save_images_to_ssm(path)

class SecureShareModel(tk.Tk):
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
        file_menu.add_command(label="Generar SSM", command=generate)
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
    app = SecureShareModel()
    app.mainloop()