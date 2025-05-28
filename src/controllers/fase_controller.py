from datetime import date
from src.supabase_manager import supabase
from src.controllers.evento_controller import buscar_evento_por_nombre

def obtener_fases_ordenadas():
    res = supabase.table("fase").select("*").order("num_fase").execute()
    return res.data if res.data else []

def insertar_fase(nombre_analisis, nombre_bd, descripcion, posicion, id_evento_inicio, id_evento_fin):
    fases = obtener_fases_ordenadas()

    es_ultima = posicion >= len(fases) + 1
    if es_ultima:
        num_fase = len(fases) + 1
        if fases:
            supabase.table("fase").update({"ultimo": False}).eq("id", fases[-1]["id"]).execute()
    else:
        for fase in fases[::-1]:
            if fase["num_fase"] >= posicion:
                supabase.table("fase").update({"num_fase": fase["num_fase"] + 1}).eq("id", fase["id"]).execute()
        num_fase = posicion

    nueva_fase = {
        "nombre_analisis": nombre_analisis,
        "nombre_bd": nombre_bd,
        "descripcion": descripcion,
        "ultimo": es_ultima,
        "fecha_inicio": date.today().isoformat(),
        "fecha_fin": "9999-12-31",
        "activo": True,
        "num_fase": num_fase
    }

    try:
        result = supabase.table("fase").insert(nueva_fase).execute()
        id_fase = result.data[0]["id"]


        # Insertar la relación en fase_evento
        supabase.table("fase_evento").insert({
            'id_fase': id_fase,
            'id_evento_inicio': id_evento_inicio,
            'id_evento_fin': id_evento_fin
        }).execute()

        return {"ok": True, "msg": "Fase creada exitosamente con eventos asignados"}

    except Exception as e:
        return {"ok": False, "msg": f"Error al crear fase: {e}"}


def buscar_fase_por_nombre(nombre):
    result = supabase.table("fase").select("*").eq("nombre_analisis", nombre).eq("activo", True).execute()
    return result.data[0] if result.data else None

def buscar_fase_por_nombre_bd(nombre):
    result = supabase.table("fase").select("*").eq("nombre_bd", nombre).eq("activo", True).execute()
    return result.data[0] if result.data else None
    
def actualizar_fase(nombre_original, fecha_fin):
    fase_antigua = buscar_fase_por_nombre(nombre_original)
    if not fase_antigua:
        return {"ok": False, "msg": "Fase no encontrada."}

    try:
        # Si era la última, remover ese atributo
        if fase_antigua.get("ultimo", False):
            supabase.table("fase").update({"ultimo": False}).eq("id", fase_antigua["id"]).execute()

        # Marcar la fase antigua como inactiva
        supabase.table("fase").update({
            "fecha_fin": fecha_fin,
            "activo": False
        }).eq("id", fase_antigua["id"]).execute()

        return {"ok": True, "msg": "Fase actualizada (historia tipo 2 aplicada)."}
    except Exception as e:
        return {"ok": False, "msg": str(e)}
    
def obtener_fases():
    try:
        response = supabase.table("fase")\
            .select("id, nombre_analisis, nombre_bd, descripcion")\
            .eq("activo", True)\
            .execute()

        return response.data
    except Exception as e:
        print(f"Error al obtener fases: {e}")
        return []

def obtener_eventos_por_fase(id_fase: str):
    try:
        response = supabase.table("fase_evento") \
            .select("id_evento_inicio, id_evento_fin") \
            .eq("id_fase", id_fase) \
            .execute()
        
        if response.data:
            return {
                "ok": True,
                "id_evento_inicio": response.data[0]["id_evento_inicio"],
                "id_evento_fin": response.data[0]["id_evento_fin"]
            }
        else:
            return {"ok": False, "msg": "No se encontraron eventos para la fase proporcionada."}
    
    except Exception as e:
        return {"ok": False, "msg": f"Error al obtener eventos: {e}"}
