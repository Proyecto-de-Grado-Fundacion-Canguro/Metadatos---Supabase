import sys
import os
import tkinter.messagebox as messagebox

# Agregar la raíz del proyecto al path para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import customtkinter as ctk
from src.GUI.forms.evento_forms import formulario_crear_evento,formulario_editar_evento

# Tema y estilo moderno
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
for nombre in ["Variable", "Episodio", "Fase", "Evento"]:
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
acciones_variable = [
    ("Añadir Variable", lambda: messagebox.showinfo("En desarrollo", "Añadir Variable en desarrollo")),
    ("Añadir Historia a Variable", lambda: messagebox.showinfo("En desarrollo", "Historia a Variable en desarrollo")),
    ("Añadir Operación a Variable", lambda: messagebox.showinfo("En desarrollo", "Operación a Variable en desarrollo")),
    ("Añadir Variable Longitudinal", lambda: messagebox.showinfo("En desarrollo", "Variable Longitudinal en desarrollo"))
]
acciones_episodio = [
    ("Añadir Episodio", lambda: messagebox.showinfo("En desarrollo", "Añadir Episodio en desarrollo")),
    ("Editar Episodio", lambda: messagebox.showinfo("En desarrollo", "Editar Episodio en desarrollo"))
]
acciones_fase = [
    ("Añadir Fase", lambda: messagebox.showinfo("En desarrollo", "Añadir Fase en desarrollo")),
    ("Editar Fase", lambda: messagebox.showinfo("En desarrollo", "Editar Fase en desarrollo"))
]
acciones_evento = [
    ("Añadir Evento", formulario_crear_evento),  # 👈 Sin paréntesis
    ("Editar Evento", formulario_editar_evento)   # 👈 Sin paréntesis
]

agregar_botones("Variable", acciones_variable)
agregar_botones("Episodio", acciones_episodio)
agregar_botones("Fase", acciones_fase)
agregar_botones("Evento", acciones_evento)

# Ejecutar GUI
app.mainloop()
