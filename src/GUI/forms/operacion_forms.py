import sys
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.controllers.variable_controller import buscar_variable_id_por_nombre_analisis, obtener_nombres_variables
from src.controllers.variable_controller import add_operacion_a_variable

def formulario_operacion(root):
    ventana = ctk.CTkToplevel(root)
    ventana.title("Añadir Operación a Variables")
    ventana.geometry("600x600")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - 300
    y = (ventana.winfo_screenheight() // 2) - 300
    ventana.geometry(f"600x600+{x}+{y}")

    # Lista de entradas de variables
    entradas_variables = []

    frame_variables = ctk.CTkFrame(ventana)
    frame_variables.pack(pady=10)

    def crear_campo_variable():
        fila = ctk.CTkFrame(frame_variables)
        fila.pack(pady=5, fill="x")

        entrada = ctk.CTkEntry(fila, placeholder_text="Nombre de la variable", width=400)
        entrada.pack(side="left", padx=5)

        def eliminar():
            fila.destroy()
            entradas_variables.remove(entrada)

        boton_borrar = ctk.CTkButton(fila, text="❌", width=40, command=eliminar)
        boton_borrar.pack(side="left")

        entradas_variables.append(entrada)

    # Campo inicial
    crear_campo_variable()

    ctk.CTkButton(ventana, text="Añadir otra variable", command=crear_campo_variable, width=200).pack(pady=10)

    entrada_descripcion = ctk.CTkEntry(ventana, placeholder_text="Descripción de la operación", width=500, height=40)
    entrada_descripcion.pack(pady=20)

    def guardar_operacion():
        nombres = [entrada.get().strip() for entrada in entradas_variables if entrada.get().strip() != ""]
        if not nombres:
            messagebox.showerror("Error", "Debe ingresar al menos una variable")
            return

        ids = []
        for nombre in nombres:
            id_var = buscar_variable_id_por_nombre_analisis(nombre)
            if not id_var:
                messagebox.showerror("Error", f"La variable '{nombre}' no fue encontrada.")
                return
            ids.append(id_var)

        descripcion = entrada_descripcion.get().strip()
        if not descripcion:
            messagebox.showerror("Error", "Debe ingresar una descripción")
            return

        res = add_operacion_a_variable(ids, descripcion)
        if res["ok"]:
            messagebox.showinfo("Éxito", res["msg"])
            ventana.destroy()
        else:
            messagebox.showerror("Error", res["msg"])

    ctk.CTkButton(ventana, text="Guardar Operación", command=guardar_operacion, width=500, height=40).pack(pady=20)
