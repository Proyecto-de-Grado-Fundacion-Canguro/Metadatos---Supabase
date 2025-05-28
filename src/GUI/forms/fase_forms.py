import sys
import os
import tkinter as tk
from tkinter import messagebox
from datetime import date
import customtkinter as ctk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.controllers.evento_controller import obtener_eventos_existentes

from src.controllers.fase_controller import *

def formulario_crear_fase(root):
    ventana = ctk.CTkToplevel(root)
    ventana.title("Añadir Fase")
    ventana.geometry("500x600")
    ventana.grab_set()

    nombre_analisis = ctk.CTkEntry(ventana, placeholder_text="Nombre de análisis", width=400)
    nombre_analisis.pack(pady=10)

    nombre_bd = ctk.CTkEntry(ventana, placeholder_text="Nombre en base de datos", width=400)
    nombre_bd.pack(pady=10)

    descripcion = ctk.CTkEntry(ventana, placeholder_text="Descripción", width=400)
    descripcion.pack(pady=10)

    posicion = ctk.CTkEntry(ventana, placeholder_text="Número de fase (posición)", width=400)
    posicion.pack(pady=10)

    # Obtener eventos de la base de datos
    eventos = obtener_eventos_existentes()
    eventos_map = {e["nombre"]: e["id"] for e in eventos}
    nombres_eventos = list(eventos_map.keys())

    ctk.CTkLabel(ventana, text="Evento inicial").pack(pady=5)
    combo_inicio = ctk.CTkComboBox(ventana, values=nombres_eventos, width=400)
    combo_inicio.pack(pady=5)

    ctk.CTkLabel(ventana, text="Evento final").pack(pady=5)
    combo_fin = ctk.CTkComboBox(ventana, values=nombres_eventos, width=400)
    combo_fin.pack(pady=5)

    def guardar():
        try:
            pos = int(posicion.get())
        except ValueError:
            messagebox.showerror("Error", "El número de fase debe ser un número entero.")
            return

        id_evento_inicio = eventos_map.get(combo_inicio.get())
        id_evento_fin = eventos_map.get(combo_fin.get())

        if not id_evento_inicio or not id_evento_fin:
            messagebox.showerror("Error", "Debe seleccionar eventos válidos.")
            return

        res = insertar_fase(
            nombre_analisis.get(),
            nombre_bd.get(),
            descripcion.get(),
            pos,
            id_evento_inicio,
            id_evento_fin
        )

        if res["ok"]:
            messagebox.showinfo("Éxito", res["msg"])
            ventana.destroy()
        else:
            messagebox.showerror("Error", res["msg"])

    ctk.CTkButton(ventana, text="Guardar Fase", command=guardar).pack(pady=20)
def formulario_editar_fase(root):
    ventana = ctk.CTkToplevel(root)
    ventana.title("Editar Fase")
    ventana.geometry("600x600")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Buscar fase por nombre:", font=("Segoe UI", 16)).pack(pady=(20, 5))
    entrada_busqueda = ctk.CTkEntry(ventana, placeholder_text="Nombre de análisis", width=500)
    entrada_busqueda.pack(pady=10)

    # Campos de edición
    nombre_analisis = ctk.CTkEntry(ventana, placeholder_text="Nuevo nombre de análisis", width=500)
    nombre_bd = ctk.CTkEntry(ventana, placeholder_text="Nuevo nombre en BD", width=500)
    descripcion = ctk.CTkEntry(ventana, placeholder_text="Nueva descripción", width=500)
    posicion = ctk.CTkEntry(ventana, placeholder_text="Nuevo número de fase", width=500)

    for widget in [nombre_analisis, nombre_bd, descripcion, posicion]:
        widget.pack(pady=10)

    # Función de búsqueda
    def cargar_datos():
        nombre = entrada_busqueda.get().strip()
        fase = buscar_fase_por_nombre(nombre)
        if not fase:
            messagebox.showerror("Error", "Fase no encontrada.")
            return

        nombre_analisis.delete(0, tk.END)
        nombre_analisis.insert(0, fase.get("nombre_analisis", ""))

        nombre_bd.delete(0, tk.END)
        nombre_bd.insert(0, fase.get("nombre_bd", ""))

        descripcion.delete(0, tk.END)
        descripcion.insert(0, fase.get("descripcion", ""))

        posicion.delete(0, tk.END)
        posicion.insert(0, str(fase.get("num_fase", "")))

    ctk.CTkButton(ventana, text="Buscar", command=cargar_datos).pack(pady=10)

    def guardar():
        nombre_original = entrada_busqueda.get().strip()
        nuevo_nombre = nombre_analisis.get().strip()
        nuevo_bd = nombre_bd.get().strip()
        nueva_desc = descripcion.get().strip()

        try:
            nueva_pos = int(posicion.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El número de fase debe ser un número entero.")
            return

        if not (nombre_original and nuevo_nombre and nuevo_bd and nueva_desc):
            messagebox.showerror("Error", "Todos los campos deben estar completos.")
            return

        hoy = date.today().isoformat()

        # Historia tipo 2: marcar antigua como inactiva
        desactivar = actualizar_fase(nombre_original, hoy)
        if not desactivar["ok"]:
            messagebox.showerror("Error", desactivar["msg"])
            return

        # Insertar nueva fase
        insertar = insertar_fase(nuevo_nombre, nuevo_bd, nueva_desc, nueva_pos)
        if insertar["ok"]:
            messagebox.showinfo("Éxito", insertar["msg"])
            ventana.destroy()
        else:
            messagebox.showerror("Error", insertar["msg"])

    ctk.CTkButton(ventana, text="Guardar Cambios", command=guardar).pack(pady=30)
