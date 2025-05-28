import sys
import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.controllers.evento_controller import obtener_nombres_eventos, buscar_evento_id_por_nombre
from src.controllers.episodio_controller import insertar_episodio, buscar_episodio_por_nombre, actualizar_episodio


def formulario_crear_episodio(root):
    ventana = ctk.CTkToplevel(root)
    ventana.title("Crear Episodio")
    ventana.geometry("600x600")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Nombre de análisis").pack(pady=10)
    nombre_analisis = ctk.CTkEntry(ventana, width=500)
    nombre_analisis.pack()

    ctk.CTkLabel(ventana, text="Nombre en BD").pack(pady=10)
    nombre_bd = ctk.CTkEntry(ventana, width=500)
    nombre_bd.pack()

    ctk.CTkLabel(ventana, text="Descripción").pack(pady=10)
    descripcion = ctk.CTkEntry(ventana, width=500)
    descripcion.pack()

    eventos = obtener_nombres_eventos()

    ctk.CTkLabel(ventana, text="Evento Inicial").pack(pady=10)
    var_inicio = ctk.StringVar()
    dropdown_inicio = ctk.CTkOptionMenu(ventana, values=eventos, variable=var_inicio, width=500)
    dropdown_inicio.pack()

    ctk.CTkLabel(ventana, text="Evento Final").pack(pady=10)
    var_fin = ctk.StringVar()
    dropdown_fin = ctk.CTkOptionMenu(ventana, values=eventos, variable=var_fin, width=500)
    dropdown_fin.pack()

    def guardar():
        nombre = nombre_analisis.get().strip()
        bd = nombre_bd.get().strip()
        desc = descripcion.get().strip()
        ev_inicio = var_inicio.get()
        ev_fin = var_fin.get()

        if not all([nombre, bd, desc, ev_inicio, ev_fin]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        id_inicio = buscar_evento_id_por_nombre(ev_inicio)
        id_fin = buscar_evento_id_por_nombre(ev_fin)

        res = insertar_episodio(nombre, bd, desc, id_fin, id_inicio)
        if res["ok"]:
            messagebox.showinfo("Éxito", res["msg"])
            ventana.destroy()
        else:
            messagebox.showerror("Error", res["msg"])

    ctk.CTkButton(ventana, text="Guardar", command=guardar, width=500).pack(pady=20)


def formulario_editar_episodio(root):
    ventana = ctk.CTkToplevel(root)
    ventana.title("Editar Episodio")
    ventana.geometry("600x700")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Buscar episodio por nombre de análisis").pack(pady=10)
    entrada_busqueda = ctk.CTkEntry(ventana, width=500)
    entrada_busqueda.pack()

    nombre_analisis = ctk.CTkEntry(ventana, placeholder_text="Nuevo nombre análisis", width=500)
    nombre_bd = ctk.CTkEntry(ventana, placeholder_text="Nuevo nombre en BD", width=500)
    descripcion = ctk.CTkEntry(ventana, placeholder_text="Nueva descripción", width=500)

    nombre_analisis.pack(pady=10)
    nombre_bd.pack(pady=10)
    descripcion.pack(pady=10)

    eventos = obtener_nombres_eventos()
    var_inicio = ctk.StringVar()
    var_fin = ctk.StringVar()

    ctk.CTkLabel(ventana, text="Evento Inicial").pack()
    dropdown_inicio = ctk.CTkOptionMenu(
        ventana,
        values=eventos,
        variable=var_inicio,
        width=500,
        fg_color="#2a2a2a",
        button_color="#3a3a3a",
        text_color="white",
        dropdown_fg_color="#2a2a2a",
        dropdown_text_color="white"
    )
    dropdown_inicio.pack()
    dropdown_inicio.pack(pady=5)

    ctk.CTkLabel(ventana, text="Evento Final").pack()
    dropdown_fin = ctk.CTkOptionMenu(ventana,
        values=eventos,
        variable=var_inicio,
        width=500,
        fg_color="#2a2a2a",
        button_color="#3a3a3a",
        text_color="white",
        dropdown_fg_color="#2a2a2a",
        dropdown_text_color="white")
    dropdown_fin.pack(pady=5)

    def cargar():
        nombre = entrada_busqueda.get().strip()
        epi = buscar_episodio_por_nombre(nombre)
        if not epi:
            messagebox.showerror("Error", "Episodio no encontrado")
            return

        nombre_analisis.delete(0, tk.END)
        nombre_analisis.insert(0, epi["nombre_analisis"])
        nombre_bd.delete(0, tk.END)
        nombre_bd.insert(0, epi["nombre_bd"])
        descripcion.delete(0, tk.END)
        descripcion.insert(0, epi["descripcion"])

    ctk.CTkButton(ventana, text="Buscar", command=cargar).pack(pady=10)

    def guardar():
        original = entrada_busqueda.get().strip()
        nuevo_nombre = nombre_analisis.get().strip()
        nuevo_bd = nombre_bd.get().strip()
        nueva_desc = descripcion.get().strip()
        id_inicio = buscar_evento_id_por_nombre(var_inicio.get())
        id_fin = buscar_evento_id_por_nombre(var_fin.get())

        if not all([original, nuevo_nombre, nuevo_bd, nueva_desc, id_inicio, id_fin]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        res = actualizar_episodio(original, nuevo_nombre, nuevo_bd, nueva_desc, id_inicio, id_fin)
        if res["ok"]:
            messagebox.showinfo("Éxito", res["msg"])
            ventana.destroy()
        else:
            messagebox.showerror("Error", res["msg"])

    ctk.CTkButton(ventana, text="Guardar cambios", command=guardar, width=500).pack(pady=20)
