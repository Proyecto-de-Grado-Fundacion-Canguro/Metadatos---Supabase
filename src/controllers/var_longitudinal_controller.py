from datetime import date
from src.supabase_manager import supabase

def buscar_grupo_vl_id_por_nombre(nombre):
    try:
        response = supabase.table("grupo_variable_longitudinal").select("id").eq("nombre", nombre).limit(1).execute()
        if response.data:
            return response.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error al buscar grupo variable longitudinal: {e}")
        return None
    
def obtener_ids_variables_por_grupo(id_grupo_variable, supabase):
    try:
        response = supabase.table("puente_variable_longitudinal").select("id_variable_longitudinal").eq("id_grupo_variable", id_grupo_variable).execute()
        data = response.data
        return [item['id_variable_longitudinal'] for item in data]
    except Exception as e:
        print(f"Error al consultar Supabase: {e}")
        return []
    
def editar_grupo_variable_longitudinal(nombre_grupo: str,nombre_variable_bd: str,fase: str,abcisa: str):

    try:
        # Buscar ID del grupo
        id_grupo = buscar_grupo_vl_id_por_nombre(nombre_grupo)

        # Buscar ID de la variable por nombre_bd
        variable_query = supabase.table("variable").select("id").eq("nombre_bd", nombre_variable_bd).execute()
        if not variable_query.data:
            raise ValueError("No se encontró la variable con ese nombre_bd.")

        id_variable = variable_query.data[0]["id"]

        # Insertar en la tabla 
        descripcion = f"{nombre_grupo} - {fase}"

        supabase.table("puente_variable_longitudinal").insert({
            "id_grupo_variable": id_grupo,
            "id_variable_longitudinal": id_variable,
            "descripcion": descripcion,
            "abcisa": abcisa
        }).execute()

        print("Variable añadida exitosamente al grupo.")
        return {"ok": True, "msg": "Variable añadida exitosamente al grupo."}

    except Exception as e:
        print(f"Error al editar grupo: {e}")
        return {"ok": False, "msg": str(e)}
    
def add_grupo(nombre):
    data = {
        'nombre': nombre
    }
    try:
        # Inserta el grupo
        supabase.table("grupo_variable_longitudinal").insert(data).execute()
        
        # Consulta el id recién insertado por nombre
        response = supabase.table("grupo_variable_longitudinal").select("id").eq("nombre", nombre).execute()
        if response.data:
            grupo_id = response.data[0]['id']
            return {"ok": True, "msg": "Grupo VL creado exitosamente.", "id": grupo_id}
        else:
            return {"ok": False, "msg": "Grupo creado pero no se pudo obtener el ID.", "id": None}
    except Exception as e:
        return {"ok": False, "msg": str(e), "id": None}

