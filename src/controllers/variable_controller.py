from src.supabase_manager import supabase

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