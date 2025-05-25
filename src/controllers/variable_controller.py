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