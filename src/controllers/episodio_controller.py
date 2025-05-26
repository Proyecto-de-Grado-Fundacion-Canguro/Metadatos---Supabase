from datetime import date
from src.supabase_manager import supabase

def buscar_episodio_por_nombre(nombre_analisis):
    result = supabase.table("episodio").select("*").eq("nombre_analisis", nombre_analisis).eq("activo", True).execute()
    return result.data[0] if result.data else None

def insertar_episodio(nombre_analisis,nombre_bd,descripcion,id_fin,id_inicio):
    data={
        'descripcion':descripcion,
        "fecha_inicio": date.today().isoformat(),
        "fecha_fin": "9999-12-31",
        "activo": True,
        'nombre_analisis':nombre_analisis,
        'nombre_bd':nombre_bd,
        'id_evento_inicio':id_inicio,
        'id_evento_fin':id_fin
    }
    try:
        supabase.table("episodio").insert(data).execute()
        return {"ok": True, "msg": "Episodio creado exitosamente."}
    except Exception as e:
        return {"ok": False, "msg": str(e)}
    
def actualizar_episodio(nombre_analisis_original, nuevo_nombre_analisis, nuevo_nombre_bd, nueva_desc, id_fin, id_inicio):
    episodio = buscar_episodio_por_nombre(nombre_analisis_original)
    if not episodio:
        return {"ok": False, "msg": "Episodio no encontrado."}

    hoy = date.today().isoformat()

    try:
        supabase.table("episodio").update({
            "fecha_fin": hoy,
            "activo": False
        }).eq("id", episodio["id"]).execute()

        nuevo_episodio = {
            'nombre_analisis': nuevo_nombre_analisis,
            'nombre_bd': nuevo_nombre_bd,
            'descripcion': nueva_desc,
            'id_evento_inicio': id_inicio,
            'id_evento_fin': id_fin,
            'fecha_inicio': hoy,
            'fecha_fin': "9999-12-31",
            'activo': True
        }

        supabase.table("episodio").insert(nuevo_episodio).execute()

        return {"ok": True, "msg": "Episodio actualizado exitosamente (historia tipo 2)."}

    except Exception as e:
        return {"ok": False, "msg": f"Error al actualizar episodio: {e}"}