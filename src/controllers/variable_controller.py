from src.supabase_manager import supabase
from datetime import date

def obtener_nombres_variables():
    response = supabase.table("variable").select("nombre_analisis").execute()
    if response.data:
        return [item["nombre_analisis"] for item in response.data]
    return []

def obtener_variables_analisis():
    """Retorna una lista con los nombres de análisis de las variables"""
    response = supabase.table("variable").select("id, nombre_analisis").execute()
    if response.data:
        return response.data
    return []

def buscar_variable_id_por_nombre_analisis(nombre_analisis):
    response = supabase.table("variable").select("id").eq("nombre_analisis", nombre_analisis).limit(1).execute()
    if response.data:
        return response.data[0]["id"]
    return None


def add_grupo(descripcion):
    data = {"descripcion": descripcion}
    response = supabase.table("grupo_operacion").insert(data).execute()

    if response.data and len(response.data) > 0:
        return response.data[0]["id"]  
    else:
        raise Exception("Error al crear el grupo de operación.")
    
def add_operacion_a_variable(ids_variable, descripcion):
    try:
        id_grupo = add_grupo(descripcion)

        data_puentes = []
        for id_var in ids_variable:
            data_puentes.append({
                "id_grupo_operacion": id_grupo,
                "id_variable": id_var
            })

            supabase.table("hecho_registrar_variable")\
                .update({"id_grupo_operacion": id_grupo})\
                .eq("id_variable", id_var)\
                .execute()

        supabase.table("puente_variable_operacion").insert(data_puentes).execute()

        return {"ok": True, "msg": "Operación creada con éxito"}

    except Exception as e:
        return {"ok": False, "msg": f"Error al crear operación: {e}"}
    
#-----------------Funcionalidades relacionada a historia---------------------------------------
def convertir_variable_a_cambiante(nombre_variable, variable_inicio, variable_fin,variable_activa,activa=True):
    try:
        id_var = buscar_variable_id_por_nombre_analisis(nombre_variable)
        id_inicio = buscar_variable_id_por_nombre_analisis(variable_inicio)
        id_fin = buscar_variable_id_por_nombre_analisis(variable_fin)

        if not all([id_var, id_inicio, id_fin]):
            return {"ok": False, "msg": "Alguna de las variables no fue encontrada."}

        # Paso 1: Marcar la variable como no básica
        supabase.table("variable")\
            .update({"basica": False})\
            .eq("id", id_var)\
            .execute()

        # Paso 2: Insertar historia inicial
        supabase.table("variable_cambiante").insert({
            "id": id_var,
            "variable_fecha_inicio": id_inicio,
            "variable_fecha_fin": id_fin,
            "activa": activa
        }).execute()

        # Paso 3: Recuperar el nuevo id_historia
        res = supabase.table("variable_cambiante")\
            .select("id_historia")\
            .eq("id", id_var)\
            .eq("variable_fecha_inicio", id_inicio)\
            .eq("variable_fecha_fin", id_fin)\
            .order("id_historia", desc=True)\
            .limit(1)\
            .execute()

        if not res.data:
            return {"ok": False, "msg": "No se pudo recuperar el ID de historia recién creada."}

        nuevo_id = res.data[0]["id_historia"]

        # Paso 4: Establecer esta historia como la activa (en el mismo registro y en los demás)
        supabase.table("variable_cambiante")\
            .update({"variable_activa": nuevo_id})\
            .eq("id", id_var)\
            .execute()

        return {"ok": True, "msg": "Variable convertida a cambiante correctamente."}

    except Exception as e:
        return {"ok": False, "msg": str(e)}
    
def agregar_historia_variable_cambiante(nombre_variable, variable_inicio, variable_fin,activa=True):
  try:
        id_var = buscar_variable_id_por_nombre_analisis(nombre_variable)
        id_inicio = buscar_variable_id_por_nombre_analisis(variable_inicio)
        id_fin = buscar_variable_id_por_nombre_analisis(variable_fin)

        if not all([id_var, id_inicio, id_fin]):
            return {"ok": False, "msg": "Alguna de las variables no fue encontrada."}

        # Desactivar las historias anteriores (activa = False)
        supabase.table("variable_cambiante")\
            .update({"activa": False})\
            .eq("id", id_var)\
            .execute()

        # Insertar la nueva historia (no pasamos id_historia)
        supabase.table("variable_cambiante").insert({
            "id": id_var,
            "variable_fecha_inicio": id_inicio,
            "variable_fecha_fin": id_fin,
            "activa": activa
        }).execute()

        # Recuperar el id_historia generado (último insertado)
        res = supabase.table("variable_cambiante")\
            .select("id_historia")\
            .eq("id", id_var)\
            .eq("variable_fecha_inicio", id_inicio)\
            .eq("variable_fecha_fin", id_fin)\
            .order("id_historia", desc=True)\
            .limit(1)\
            .execute()

        if not res.data:
            return {"ok": False, "msg": "No se pudo recuperar el ID de la nueva historia."}

        nuevo_id = res.data[0]["id_historia"]

        # Actualizar todas las historias de esta variable con variable_activa = nuevo_id
        supabase.table("variable_cambiante")\
            .update({"variable_activa": nuevo_id})\
            .eq("id", id_var)\
            .execute()

        return {"ok": True, "msg": "Nueva historia añadida correctamente."}

  except Exception as e:
        return {"ok": False, "msg": str(e)}
  
def obtener_variables_tipo_fecha():
    try:
        response = supabase.table("variable")\
            .select("id, nombre_bd, nombre_analisis, tipo_dato")\
            .filter("tipo_dato", "ilike", "DATE%")\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"Error al obtener variables tipo fecha: {e}")
        return []

def obtener_nombres_variables_basicas():
    try:
        response = supabase.table("variable")\
            .select("nombre_analisis")\
            .eq("basica", True)\
            .execute()

        return [v["nombre_analisis"] for v in response.data if v.get("nombre_analisis")]
    except Exception as e:
        print(f"Error al obtener variables básicas: {e}")
        return []


def obtener_nombres_variables_cambiantes():
    try:
        res = supabase.table("variable_cambiante")\
                      .select("id")\
                      .execute()

        ids_unicos = list(set([v["id"] for v in res.data if v.get("id")]))

        if not ids_unicos:
            return []

        variables = supabase.table("variable")\
                            .select("nombre_analisis")\
                            .in_("id", ids_unicos)\
                            .execute()

        return [v["nombre_analisis"] for v in variables.data if v.get("nombre_analisis")]

    except Exception as e:
        print(f"Error al obtener variables cambiantes: {e}")
        return []

