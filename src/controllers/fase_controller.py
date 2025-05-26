from datetime import date
from src.supabase_manager import supabase

def obtener_fases_ordenadas():
    res = supabase.table("fase").select("*").order("num_fase").execute()
    return res.data if res.data else []

def insertar_fase(nombre_analisis, nombre_bd, descripcion, posicion):
    fases = obtener_fases_ordenadas()

    # Validar si es última posición
    es_ultima = posicion >= len(fases) + 1
    if es_ultima:
        num_fase = len(fases) + 1
        # Cambiar la anterior última a ultimo=False si existe
        if fases:
            supabase.table("fase").update({"ultimo": False}).eq("id", fases[-1]["id"]).execute()
    else:
        # Reordenar fases a partir de la posición
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
        supabase.table("fase").insert(nueva_fase).execute()
        return {"ok": True, "msg": "Fase creada exitosamente"}
    except Exception as e:
        return {"ok": False, "msg": f"Error al crear fase: {e}"}

def buscar_fase_por_nombre(nombre):
    result = supabase.table("fase").select("*").eq("nombre_analisis", nombre).eq("activo", True).execute()
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
