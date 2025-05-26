import sys
import os
import tkinter.messagebox as messagebox

# Agregar la raíz del proyecto al path para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import customtkinter as ctk
from src.GUI.forms.evento_forms import formulario_crear_evento, formulario_editar_evento
from src.GUI.forms.diccionario_forms import formulario_diccionario
from src.GUI.forms.operacion_forms import formulario_operacion
from src.GUI.forms.fase_forms import formulario_editar_fase,formulario_crear_fase
from src.GUI.forms.episodio_forms import formulario_crear_episodio, formulario_editar_episodio
from src.GUI.forms.vls_form import abrir_formulario_puente_variable

# Tema y estilo 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Ventana principal
app = ctk.CTk()
app.title("Administrador de Datos Supabase")
app.geometry("800x600")

# Pestañas (Tabview)
tabs = ctk.CTkTabview(app)
tabs.pack(padx=20, pady=20, fill="both", expand=True)

# Crear pestañas
for nombre in ["Diccionario", "Variable", "Episodio", "Fase", "Evento", "Variable Longitudinal"]:
    tabs.add(nombre)

def agregar_botones(tab_name, acciones):
    frame = tabs.tab(tab_name)
    ctk.CTkLabel(frame, text=f"Operaciones sobre {tab_name}s", font=("Segoe UI", 16)).pack(pady=(10, 20))
    for texto, comando in acciones:
        def inner(nombre=texto, cmd=comando):
            if callable(cmd):
                try:
                    cmd()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            else:
                messagebox.showinfo("En desarrollo", f"La funcionalidad '{nombre}' está en desarrollo.")

        ctk.CTkButton(frame, text=texto, command=inner).pack(pady=8)

# Botones para cada pestaña
acciones_diccionario = [
    ("Cargar diccionario", lambda: formulario_diccionario(app))
]
acciones_variable = [
    ("Añadir Variable", lambda: messagebox.showinfo("En desarrollo", "Añadir Variable en desarrollo")),
    ("Añadir Historia a Variable", lambda: messagebox.showinfo("En desarrollo", "Historia a Variable en desarrollo")),
    ("Añadir Operación a Variable", lambda: formulario_operacion(app))
]
acciones_episodio = [
    ("Añadir Episodio", lambda: formulario_crear_episodio(app)),
    ("Editar Episodio", lambda: formulario_editar_episodio(app))
]
acciones_fase = [
    ("Añadir Fase", lambda: formulario_crear_fase(app)),
    ("Editar Fase", lambda: formulario_editar_fase(app))
]
acciones_evento = [
    ("Añadir Evento", lambda: formulario_crear_evento),
    ("Editar Evento", lambda: formulario_editar_evento)
]

acciones_vls=[
    ("Añadir Variable a Grupo Longitudinal",lambda: abrir_formulario_puente_variable()),
    ("Añadir Grupo Longitudinal", lambda: messagebox.showinfo("En desarrollo", "Añadir Variable en desarrollo"))
]

agregar_botones("Diccionario", acciones_diccionario)
agregar_botones("Variable", acciones_variable)
agregar_botones("Episodio", acciones_episodio)
agregar_botones("Fase", acciones_fase)
agregar_botones("Evento", acciones_evento)
agregar_botones("Variable Longitudinal", acciones_vls)

# Ejecutar GUI
app.mainloop()
