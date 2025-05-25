import sys
import os
import tkinter as tk
from tkinter import messagebox
from datetime import date
import customtkinter as ctk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.controllers.evento_controller import crear_evento, actualizar_evento, buscar_evento_por_nombre
from src.controllers.variable_controller import obtener_nombres_variables

def formulario_crear_evento():
    ventana = ctk.CTkToplevel()
    ventana.title("Añadir Evento")
    ventana.geometry("600x600")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - (600 // 2)
    y = (ventana.winfo_screenheight() // 2) - (600 // 2)
    ventana.geometry(f"600x600+{x}+{y}")

    nombre_entry = ctk.CTkEntry(ventana, placeholder_text="Nombre del evento", width=500, height=40)
    nombre_entry.pack(pady=20)

    descripcion_entry = ctk.CTkEntry(ventana, placeholder_text="Descripción", width=500, height=40)
    descripcion_entry.pack(pady=20)

    variables = obtener_nombres_variables()
    variable_entry = ctk.CTkEntry(ventana, placeholder_text="Buscar variable...", width=500, height=40)
    variable_entry.pack(pady=20)

    sugerencias_label = ctk.CTkLabel(ventana, text="", text_color="gray", font=("Segoe UI", 14))
    sugerencias_label.pack()

    def validar_variable(_):
        texto = variable_entry.get().strip().lower()
        if texto == "":
            sugerencias_label.configure(text="Variable no requerida", text_color="gray")
            return
        coincidencias = [v for v in variables if texto in v.lower()]
        if coincidencias:
            sugerencias_label.configure(text=f"Sugerencias: {', '.join(coincidencias[:5])}", text_color="gray")
        else:
            sugerencias_label.configure(text="⚠️ No hay coincidencias", text_color="red")

    variable_entry.bind("<KeyRelease>", validar_variable)

    ctk.CTkButton(
        ventana,
        text="Guardar",
        command=lambda: guardar(nombre_entry, descripcion_entry, variable_entry, variables, ventana),
        width=500,
        height=40
    ).pack(pady=40)

def guardar(nombre_entry, descripcion_entry, variable_entry, lista_variables, ventana):
    nombre = nombre_entry.get().strip()
    descripcion = descripcion_entry.get().strip()
    nombre_variable = variable_entry.get().strip()

    if not (nombre and descripcion):
        messagebox.showerror("Error", "El nombre y la descripción son obligatorios.")
        return

    if nombre_variable and nombre_variable not in lista_variables:
        messagebox.showerror("Error", "La variable ingresada no existe.")
        return

    variable_final = nombre_variable if nombre_variable else None

    res = crear_evento(nombre, descripcion, variable_final)
    if res["ok"]:
        messagebox.showinfo("Éxito", res["msg"])
        ventana.destroy()
    else:
        messagebox.showerror("Error", res["msg"])

def formulario_editar_evento():
    ventana = ctk.CTkToplevel()
    ventana.title("Editar Evento")
    ventana.geometry("600x700")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - 300
    y = (ventana.winfo_screenheight() // 2) - 350
    ventana.geometry(f"600x700+{x}+{y}")

    ctk.CTkLabel(ventana, text="Buscar evento por nombre:", font=("Segoe UI", 16)).pack(pady=(20, 10))
    entrada_busqueda = ctk.CTkEntry(ventana, width=500, height=40)
    entrada_busqueda.pack(pady=(0, 10))

    entrada_nombre = ctk.CTkEntry(ventana, placeholder_text="Nuevo nombre", width=500, height=40)
    entrada_descripcion = ctk.CTkEntry(ventana, placeholder_text="Nueva descripción", width=500, height=40)
    variable_seleccionada = ctk.StringVar()
    dropdown = ctk.CTkOptionMenu(
        ventana,
        values=[],
        variable=variable_seleccionada,
        width=500,
        height=40,
        font=("Segoe UI", 16),
        dropdown_font=("Segoe UI", 16)
    )

    def cargar_datos():
        nombre_buscar = entrada_busqueda.get().strip()
        evento = buscar_evento_por_nombre(nombre_buscar)
        if not evento:
            messagebox.showerror("Error", "Evento no encontrado")
            return

        entrada_nombre.delete(0, tk.END)
        entrada_nombre.insert(0, evento["nombre"])

        entrada_descripcion.delete(0, tk.END)
        entrada_descripcion.insert(0, evento.get("descripcion", ""))

        variables = obtener_nombres_variables()
        dropdown.configure(values=variables)

        variable_actual = next((v for v in variables if v == evento.get("nombre_variable", "")), variables[0])
        variable_seleccionada.set(variable_actual)

    ctk.CTkButton(ventana, text="Buscar", command=cargar_datos, width=500, height=40).pack(pady=10)

    entrada_nombre.pack(pady=20)
    entrada_descripcion.pack(pady=20)
    ctk.CTkLabel(ventana, text="Variable asociada:", font=("Segoe UI", 16)).pack(pady=(10, 5))
    dropdown.pack(pady=(0, 30))

    def guardar_cambios():
        nombre_original = entrada_busqueda.get().strip()
        nuevo_nombre = entrada_nombre.get().strip()
        nueva_desc = entrada_descripcion.get().strip()
        nueva_variable = variable_seleccionada.get().strip()

        if not (nombre_original and nuevo_nombre and nueva_desc and nueva_variable):
            messagebox.showerror("Error", "Todos los campos deben estar llenos.")
            return

        # Historia tipo 2: marcar como inactivo el anterior y crear una nueva fila
        hoy = date.today().isoformat()
        actualizar_evento(nombre_original, nuevo_nombre, nueva_desc, nueva_variable, fecha_fin=hoy)
        crear_evento(nuevo_nombre, nueva_desc, nueva_variable)

        messagebox.showinfo("Éxito", "Evento actualizado con historial tipo 2.")
        ventana.destroy()

    ctk.CTkButton(ventana, text="Guardar cambios", command=guardar_cambios, width=500, height=40).pack(pady=10)
