import sys
import os
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from src.uploader import charge_all_csv
from src.config import set_dict_paths

# Variables globales para almacenar las rutas
ruta_diccionario = None
ruta_longitudinales = None

def formulario_diccionario(root):
    global ruta_diccionario, ruta_longitudinales

    ventana = ctk.CTkToplevel(root)
    ventana.title("Cargar Diccionario")
    ventana.geometry("500x400")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - 250
    y = (ventana.winfo_screenheight() // 2) - 200
    ventana.geometry(f"500x400+{x}+{y}")

    label_dic = ctk.CTkLabel(ventana, text="Archivo Diccionario: No seleccionado")
    label_dic.pack(pady=10)

    def seleccionar_diccionario():
        nonlocal label_dic
        archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
        if archivo:
            global ruta_diccionario
            ruta_diccionario = archivo
            label_dic.configure(text=f"Diccionario: {os.path.basename(archivo)}")

    btn_dic = ctk.CTkButton(ventana, text="Seleccionar Diccionario", command=seleccionar_diccionario)
    btn_dic.pack(pady=10)

    label_long = ctk.CTkLabel(ventana, text="Archivo Variables Longitudinales: No seleccionado")
    label_long.pack(pady=10)

    def seleccionar_longitudinal():
        nonlocal label_long
        archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
        if archivo:
            global ruta_longitudinales
            ruta_longitudinales = archivo
            label_long.configure(text=f"Longitudinales: {os.path.basename(archivo)}")

    btn_long = ctk.CTkButton(ventana, text="Seleccionar Longitudinales", command=seleccionar_longitudinal)
    btn_long.pack(pady=10)

    spinner = ctk.CTkLabel(ventana, text="", font=("Segoe UI", 16))
    spinner.pack(pady=(20, 10))

    label_estado = ctk.CTkLabel(ventana, text="")
    label_estado.pack(pady=(0, 10))

    def cargar_archivos():
        if not ruta_diccionario or not ruta_longitudinales:
            messagebox.showerror("Error", "Debe seleccionar ambos archivos.")
            return

        try:
            label_estado.configure(text="Procesando datos...", text_color="gray")
            spinner.configure(text="⏳")
            ventana.update_idletasks()

            set_dict_paths(ruta_diccionario, ruta_longitudinales)
            charge_all_csv()

            spinner.configure(text="")
            label_estado.configure(text="Carga completada con éxito", text_color="green")
            messagebox.showinfo("Éxito", "Datos cargados exitosamente")
            ventana.destroy()
        except Exception as e:
            spinner.configure(text="")
            label_estado.configure(text="Error al cargar los datos", text_color="red")
            messagebox.showerror("Error al cargar", str(e))

    ctk.CTkButton(ventana, text="Cargar Datos", command=cargar_archivos, width=300, height=40).pack(pady=20)
