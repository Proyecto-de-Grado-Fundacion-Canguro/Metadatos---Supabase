import customtkinter as ctk
import tkinter.messagebox as mb

from src.supabase_manager import supabase
from src.controllers.var_longitudinal_controller import buscar_grupo_vl_id_por_nombre,editar_grupo_variable_longitudinal,add_grupo
from src.controllers.variable_controller import obtener_nombres_variables

def add_variable_grupo():
    ventana = ctk.CTkToplevel()
    ventana.title("Asignar Variable Longitudinal a Grupo")
    ventana.geometry("700x500")

    # Centrar y mantener al frente
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    try:
        grupos = supabase.table("grupo_variable_longitudinal").select("nombre").execute().data
        nombres_grupos = [g['nombre'] for g in grupos]
        nombres_variables = obtener_nombres_variables()
    except Exception as e:
        mb.showerror("Error", f"No se pudo cargar información: {e}")
        ventana.destroy()
        return

    ctk.CTkLabel(ventana, text="Selecciona un grupo").pack(pady=5)
    combo_grupos = ctk.CTkComboBox(ventana, values=nombres_grupos, width=400)
    combo_grupos.pack(pady=5)

    lista_variables = ctk.CTkTextbox(ventana, width=650, height=100)
    lista_variables.pack(pady=10)
    lista_variables.configure(state="disabled")

    frame_form = ctk.CTkFrame(ventana)
    frame_form.pack(pady=10)

    ctk.CTkLabel(frame_form, text="Variable").grid(row=0, column=0, padx=10, pady=5)
    combo_variable = ctk.CTkComboBox(frame_form, values=nombres_variables, width=300)
    combo_variable.grid(row=0, column=1, padx=10)

    ctk.CTkLabel(frame_form, text="Fase").grid(row=1, column=0, padx=10, pady=5)
    entry_fase = ctk.CTkEntry(frame_form, width=300)
    entry_fase.grid(row=1, column=1)

    ctk.CTkLabel(frame_form, text="Abcisa").grid(row=2, column=0, padx=10, pady=5)
    entry_abcisa = ctk.CTkEntry(frame_form, width=300)
    entry_abcisa.grid(row=2, column=1)

    def mostrar_variables_asociadas(nombre_grupo):
        lista_variables.configure(state="normal")
        lista_variables.delete("1.0", "end")

        try:
            grupo_id = buscar_grupo_vl_id_por_nombre(nombre_grupo)
            res = supabase.table("puente_variable_longitudinal")\
                .select("id_variable_longitudinal, abcisa, descripcion")\
                .eq("id_grupo_variable", grupo_id).execute().data

            if not res:
                lista_variables.insert("end", "No hay variables asociadas a este grupo.")
            else:
                salida = "Variables asociadas:\n\n"
                for var in res:
                    salida += f"- {var['descripcion']} (abcisa: {var['abcisa']})\n"
                lista_variables.insert("end", salida)

        except Exception as e:
            lista_variables.insert("end", f"Error al consultar: {e}")

        lista_variables.configure(state="disabled")

    def al_cambiar_grupo(event=None):
        grupo = combo_grupos.get()
        if grupo:
            mostrar_variables_asociadas(grupo)

    combo_grupos.configure(command=al_cambiar_grupo)

    def guardar():
        grupo = combo_grupos.get()
        variable = combo_variable.get()
        fase = entry_fase.get().strip()
        abcisa = entry_abcisa.get().strip()

        if not grupo or not variable or not fase or not abcisa:
            mb.showwarning("Campos vacíos", "Por favor completa todos los campos.")
            return

        resultado = editar_grupo_variable_longitudinal(
            supabase, grupo, variable, fase, abcisa, buscar_grupo_vl_id_por_nombre
        )

        if resultado["ok"]:
            mb.showinfo("Éxito", resultado["msg"])
            entry_fase.delete(0, 'end')
            entry_abcisa.delete(0, 'end')
            mostrar_variables_asociadas(grupo)
        else:
            mb.showerror("Error", resultado["msg"])

    ctk.CTkButton(ventana, text="Guardar Variable", command=guardar).pack(pady=10)

    # Preselección y carga inicial
    if nombres_grupos:
        combo_grupos.set(nombres_grupos[0])
        mostrar_variables_asociadas(nombres_grupos[0])

def abrir_crear_grupo_y_variables():
    ventana = ctk.CTkToplevel()
    ventana.title("Crear Grupo VL y Asignar Variables")
    ventana.geometry("750x650")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    entradas_variables = []

    # Campo para nombre del grupo
    ctk.CTkLabel(ventana, text="Nombre del nuevo grupo").pack(pady=10)
    entry_nombre_grupo = ctk.CTkEntry(ventana, width=400, placeholder_text="Ej: VL_Weight")
    entry_nombre_grupo.pack(pady=5)

    # Frame para los campos de variables
    frame_variables = ctk.CTkFrame(ventana)
    frame_variables.pack(pady=10)

    nombres_variables = obtener_nombres_variables()

    def agregar_bloque_variable():
        fila = len(entradas_variables)
        frame = ctk.CTkFrame(frame_variables)
        frame.grid(row=fila, column=0, padx=5, pady=3, sticky="w")

        combo = ctk.CTkComboBox(frame, values=nombres_variables, width=180)
        combo.set("Selecciona variable")
        combo.grid(row=0, column=0, padx=5)

        fase = ctk.CTkEntry(frame, width=120, placeholder_text="Write thephase")
        fase.grid(row=0, column=1, padx=5)

        abcisa = ctk.CTkEntry(frame, width=120, placeholder_text="Write the abcise")
        abcisa.grid(row=0, column=2, padx=5)

        entradas_variables.append((combo, fase, abcisa))

    # Añadir botón "+" al lado del título
    def boton_mas():
        agregar_bloque_variable()

    frame_header = ctk.CTkFrame(ventana)
    frame_header.pack()
    ctk.CTkLabel(frame_header, text="Variables a añadir:").pack(side="left", padx=10)
    ctk.CTkButton(frame_header, text="+", width=30, command=boton_mas).pack(side="left")

    # Agregar el primer bloque
    agregar_bloque_variable()

    # Crear grupo y guardar variables
    def crear_grupo_y_guardar():
        nombre_grupo = entry_nombre_grupo.get().strip()
        if not nombre_grupo:
            mb.showwarning("Campo vacío", "Debes ingresar un nombre para el grupo.")
            return

        resultado = add_grupo(nombre_grupo)
        if not resultado["ok"]:
            mb.showerror("Error", resultado["msg"])
            return

        grupo_id = resultado["id"]
        nombre = nombre_grupo
        guardadas = 0
        errores = []

        for combo, fase_entry, abcisa_entry in entradas_variables:
            variable = combo.get()
            fase = fase_entry.get().strip()
            abcisa = abcisa_entry.get().strip()

            if not variable or not fase or not abcisa or variable == "Selecciona variable":
                errores.append("Hay campos vacíos o sin seleccionar en una de las variables.")
                continue

            r = editar_grupo_variable_longitudinal(nombre, variable, fase, abcisa)
            if r["ok"]:
                guardadas += 1
            else:
                errores.append(r["msg"])

        if guardadas:
            mb.showinfo("Éxito", f"Grupo y {guardadas} variable(s) añadidas correctamente.")
            ventana.destroy()
        elif errores:
            mb.showerror("Error", "\n".join(errores))

    # Botón final
    ctk.CTkButton(ventana, text="Crear grupo con variables", command=crear_grupo_y_guardar).pack(pady=20)