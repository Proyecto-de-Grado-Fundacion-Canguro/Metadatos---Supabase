from datetime import date
from src.supabase_manager import supabase
from src.controllers.variable_controller import buscar_variable_id_por_nombre_analisis

def crear_evento(nombre, descripcion, nombre_variable):
    id_variable = buscar_variable_id_por_nombre_analisis(nombre_variable)
    data = {
        "nombre": nombre,
        "descripcion": descripcion,
        "id_variable_fecha": id_variable,
        "fecha_inicio": date.today().isoformat(),
        "fecha_fin": "9999-12-31",
        "activo": True
    }
    try:
        supabase.table("evento").insert(data).execute()
        return {"ok": True, "msg": "Evento creado exitosamente."}
    except Exception as e:
        return {"ok": False, "msg": str(e)}

def buscar_evento_por_nombre(nombre):
    result = supabase.table("evento").select("*").eq("nombre", nombre).eq("activo", True).execute()
    return result.data[0] if result.data else None

def actualizar_evento(nombre_original, nuevo_nombre, nueva_desc, nueva_variable, fecha_fin):
    evento = buscar_evento_por_nombre(nombre_original)
    if not evento:
        return {"ok": False, "msg": "Evento no encontrado."}

    try:
        # Marcar el evento antiguo como inactivo con fecha_fin
        supabase.table("evento").update({
            "fecha_fin": fecha_fin,
            "activo": False
        }).eq("id", evento["id"]).execute()
        return {"ok": True, "msg": "Evento actualizado (marcado como inactivo)."}
    except Exception as e:
        return {"ok": False, "msg": str(e)}
