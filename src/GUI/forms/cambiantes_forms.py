import customtkinter as ctk
import tkinter.messagebox as mb
from src.supabase_manager import supabase
import tkinter as tk
from src.controllers.variable_controller import obtener_nombres_variables_basicas, obtener_variables_tipo_fecha, convertir_variable_a_cambiante
from src.controllers.variable_controller import buscar_variable_id_por_nombre_analisis, agregar_historia_variable_cambiante, obtener_nombres_variables_cambiantes

def abrir_formulario_convertir_basica():
    ventana = ctk.CTkToplevel()
    ventana.title("Convertir Variable Básica a Cambiante")
    ventana.geometry("600x400")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    # --- Cargar variables ---
    try:
        variables_basicas = obtener_nombres_variables_basicas()
        variables_fecha = obtener_variables_tipo_fecha()
        nombres_fecha = [v["nombre_analisis"] for v in variables_fecha]
    except Exception as e:
        mb.showerror("Error", f"No se pudieron cargar variables: {e}")
        ventana.destroy()
        return

    ctk.CTkLabel(ventana, text="Selecciona variable básica").pack(pady=5)
    combo_basica = ctk.CTkComboBox(ventana, values=variables_basicas, width=400)
    combo_basica.pack(pady=5)

    ctk.CTkLabel(ventana, text="Variable fecha inicio").pack(pady=5)
    combo_inicio = ctk.CTkComboBox(ventana, values=nombres_fecha, width=300)
    combo_inicio.pack(pady=5)

    ctk.CTkLabel(ventana, text="Variable fecha fin").pack(pady=5)
    combo_fin = ctk.CTkComboBox(ventana, values=nombres_fecha, width=300)
    combo_fin.pack(pady=5)

    def convertir():
        nombre_var = combo_basica.get()
        var_inicio = combo_inicio.get()
        var_fin = combo_fin.get()

        if not nombre_var or not var_inicio or not var_fin:
            mb.showwarning("Campos incompletos", "Debes seleccionar todos los campos.")
            return

        id_var = buscar_variable_id_por_nombre_analisis(nombre_var)
        if not id_var:
            mb.showerror("Error", f"No se encontró el ID de la variable '{nombre_var}'.")
            return

        resultado = convertir_variable_a_cambiante(
            nombre_variable=nombre_var,
            variable_inicio=var_inicio,
            variable_fin=var_fin,
            activa=True
        )

        if resultado["ok"]:
            mb.showinfo("Éxito", resultado["msg"])
            ventana.destroy()
        else:
            mb.showerror("Error", resultado["msg"])

    ctk.CTkButton(ventana, text="Convertir a Cambiante", command=convertir).pack(pady=20)


def abrir_formulario_agregar_historia():
    ventana = ctk.CTkToplevel()
    ventana.title("Agregar Historia a Variable Cambiante")
    ventana.geometry("650x400")
    ventana.lift()
    ventana.focus_force()
    ventana.grab_set()

    try:
        variables_cambiantes = obtener_nombres_variables_cambiantes()
        variables_cambiantes = [str(v) for v in variables_cambiantes if v]  # asegurar que sean strings
        variables_fecha = obtener_variables_tipo_fecha()
        nombres_fecha = [v["nombre_analisis"] for v in variables_fecha]
    except Exception as e:
        mb.showerror("Error", f"No se pudieron cargar datos: {e}")
        ventana.destroy()
        return

    ctk.CTkLabel(ventana, text="Selecciona variable cambiante").pack(pady=5)

    variable_cambiante_var = tk.StringVar(value="")  # inicial vacío

    if variables_cambiantes:
        variable_cambiante_var.set("")  # dejar vacío si hay opciones
        combo_var = ctk.CTkComboBox(ventana, values=variables_cambiantes, width=400, variable=variable_cambiante_var)
    else:
        mensaje_sin_variables = "No hay variables cambiantes"
        variable_cambiante_var.set(mensaje_sin_variables)
        combo_var = ctk.CTkComboBox(
            ventana,
            values=[mensaje_sin_variables],
            width=400,
            variable=variable_cambiante_var,
            state="disabled"
        )


    combo_var.pack(pady=5)

    label_inicio = ctk.CTkLabel(ventana, text="Variable inicio actual: (selecciona variable arriba)", text_color="gray")
    label_inicio.pack(pady=5)

    variable_inicio_actual = None

    def actualizar_inicio_automaticamente(nombre_var):
        nonlocal variable_inicio_actual
        try:
            id_var = buscar_variable_id_por_nombre_analisis(nombre_var)
            res = supabase.table("variable_cambiante")\
                .select("variable_fecha_fin")\
                .eq("id", id_var)\
                .eq("activa", True)\
                .limit(1)\
                .execute()

            if res.data:
                id_fecha_inicio = res.data[0]["variable_fecha_fin"]

                r = supabase.table("variable").select("nombre_analisis").eq("id", id_fecha_inicio).execute()
                if r.data:
                    variable_inicio_actual = r.data[0]["nombre_analisis"]
                    label_inicio.configure(text=f"Inicio: {variable_inicio_actual}", text_color="white")
                else:
                    variable_inicio_actual = None
                    label_inicio.configure(text="No se encontró variable_fecha_fin en variable actual", text_color="red")
            else:
                variable_inicio_actual = None
                label_inicio.configure(text="No hay historia activa para esta variable", text_color="red")
        except Exception as e:
            variable_inicio_actual = None
            label_inicio.configure(text=f"Error al consultar inicio: {e}", text_color="red")

    variable_cambiante_var.trace_add("write", lambda *_: actualizar_inicio_automaticamente(variable_cambiante_var.get()))

    ctk.CTkLabel(ventana, text="Selecciona variable fecha fin").pack(pady=5)
    combo_fin = ctk.CTkComboBox(ventana, values=nombres_fecha, width=300)
    combo_fin.pack(pady=5)

    def guardar_historia():
        nombre_variable = variable_cambiante_var.get()
        variable_fin = combo_fin.get()

        if not nombre_variable or not variable_inicio_actual or not variable_fin:
            mb.showwarning("Campos incompletos", "Selecciona una variable válida y una fecha fin.")
            return

        resultado = agregar_historia_variable_cambiante(
            nombre_variable=nombre_variable,
            variable_inicio=variable_inicio_actual,
            variable_fin=variable_fin,
            activa=True
        )

        if resultado["ok"]:
            mb.showinfo("Éxito", resultado["msg"])
            ventana.destroy()
        else:
            mb.showerror("Error", resultado["msg"])

    ctk.CTkButton(ventana, text="Agregar Historia", command=guardar_historia).pack(pady=20)