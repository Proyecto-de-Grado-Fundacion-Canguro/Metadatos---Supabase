import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controllers.hecho_controller import cargar_hecho
from src.config import set_variable_path

def formulario_cargar_hecho(root):
    ventana = ctk.CTkToplevel(root)
    ventana.title("Cargar Hechos desde Excel")
    ventana.geometry("500x250")
    ventana.grab_set()

    ruta_archivo = ctk.StringVar()

    def seleccionar_archivo():
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if archivo:
            ruta_archivo.set(archivo)
            label_ruta.configure(text=archivo)

    def cargar_archivo():
        print(f"Ruta seleccionada: {ruta_archivo.get()}")
        if not ruta_archivo.get():
            messagebox.showerror("Error", "Debe seleccionar un archivo Excel.")
            return

        try:
            set_variable_path(ruta_archivo.get())  # Se establece la ruta del archivo
            cargar_hecho()                         # Se cargan los hechos desde el archivo
            messagebox.showinfo("Éxito", "Hechos cargados correctamente.")
            ventana.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al cargar el archivo:\n{str(e)}")

    # Widgets UI
    ctk.CTkLabel(ventana, text="Carga de archivo Excel para hechos", font=("Arial", 16)).pack(pady=20)

    label_ruta = ctk.CTkLabel(ventana, text="Ningún archivo seleccionado", wraplength=400)
    label_ruta.pack(pady=5)

    ctk.CTkButton(ventana, text="Seleccionar Archivo", command=seleccionar_archivo).pack(pady=10)
    ctk.CTkButton(ventana, text="Cargar Hechos", command=cargar_archivo).pack(pady=20)
