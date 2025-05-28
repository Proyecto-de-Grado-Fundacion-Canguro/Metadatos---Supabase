from src.supabase_manager import supabase
from datetime import date

#--------------------------------Fecha----------------------------------------
def crear_fecha_hoy():
    try:
        hoy = date.today()
        id_fecha = hoy.isoformat()

        # Verificar si ya existe
        existente = supabase.table("fecha").select("id").eq("id", id_fecha).execute()
        if existente.data:
            return id_fecha

        # Insertar si no existe
        nueva_fecha = {
            "id": id_fecha,
            "fecha_date": hoy.isoformat(),
            "dia": hoy.day,
            "mes": hoy.month,
            "anio": hoy.year
        }
        supabase.table("fecha").insert(nueva_fecha).execute()
        return id_fecha

    except Exception as e:
        print(f"Error al crear fecha: {e}")
        return None

#----------------------------------------------Prefijo--------------------------------------------------------------------
def obtener_prefijos():
    try:
        response = supabase.table("prefijo").select("id, sigla, descripcion").execute()
        return [{"id": p["id"], "prefijo": p["sigla"], "descripcion": p["descripcion"]} for p in response.data]
    except Exception as e:
        print(f"Error al obtener prefijos: {e}")
        return []

def obtener_prefijo_por_sigla(sigla: str):
    try:
        respuesta = supabase.table("prefijo").select("*").eq("sigla", sigla).limit(1).execute()

        if respuesta.data:
            return respuesta.data[0]  
        else:
            return None  

    except Exception as e:
        print("Error al consultar el prefijo:", str(e))
        return None


#--------------------------------Tema interes--------------------------------------------------------------------
def agregar_tema_interes(nombre: str, descripcion: str):
    try:
        data = {"nombre": nombre, "descripcion": descripcion}
        supabase.table("tema_interes").insert(data).execute()
        return {"ok": True, "msg": "Tema de interés agregado correctamente."}
    except Exception as e:
        return {"ok": False, "msg": str(e)}
    
def obtener_temas_interes():
    try:
        response = supabase.table("tema_interes").select("id, nombre, descripcion").execute()
        return response.data
    except Exception as e:
        print(f"Error al obtener temas de interés: {e}")
        return []


def crear_grupo_tema_interes_con_temas(lista_ids_temas: list[str]):

    try:
        # Crear grupo 
        grupo_resp = supabase.table("grupo_tema_interes").insert({}).execute()
        if not grupo_resp.data:
            return {"ok": False, "msg": "No se pudo crear el grupo de temas de interés."}

        id_grupo = grupo_resp.data[0]["id"]

        # Crear registros para el puente
        registros_puente = [{
            "id_grupo_tema_interes": id_grupo,
            "id_tema_interes": tema_id
        } for tema_id in lista_ids_temas]

        if registros_puente:
            supabase.table("puente_tema_interes").insert(registros_puente).execute()

        return {"ok": True, "msg": "Grupo creado y temas asociados correctamente.", "id_grupo": id_grupo}

    except Exception as e:
        return {"ok": False, "msg": str(e)}

def buscar_tema_interes_por_nombre(nombre: str):
    try:
        result = supabase.table("tema_interes") \
            .select("id, nombre, descripcion") \
            .ilike("nombre", nombre) \
            .execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error al buscar tema de interés: {e}")
        return None

    
#-------------------------------Valor Categoria---------------------------------------------------------------------
def crear_grupo_valor_categoria_con_valores(lista_ids_valores: list[str]):
    try:
        grupo_resp = supabase.table("grupo_valor_categoria").insert({}).execute()
        if not grupo_resp.data:
            return {"ok": False, "msg": "No se pudo crear el grupo de valor categoría."}

        id_grupo = grupo_resp.data[0]["id"]

        registros_puente = [{
            "id_grupo_valor_categoria": id_grupo,
            "id_valor_categoria": valor_id
        } for valor_id in lista_ids_valores]

        if registros_puente:
            supabase.table("puente_categoria").insert(registros_puente).execute()

        return id_grupo

    except Exception as e:
        return {"ok": False, "msg": str(e)}


def agregar_valor_categoria(valor, descripcion):
    try:
        data = {
            "codificacion": valor,
            "descripcion": descripcion
        }
        result = supabase.table("valor_categoria").insert(data, returning="representation").execute()
        if result.data:
            return {
                "ok": True,
                "msg": "Valor de categoría agregado correctamente.",
                "id": result.data[0]["id"]
            }
        else:
            return {"ok": False, "msg": "No se devolvió ningún dato al insertar."}
    except Exception as e:
        return {"ok": False, "msg": str(e)}



def obtener_valores_categoria():
    try:
        res = supabase.table("valor_categoria")\
                      .select("id, id_categoria, valor, descripcion")\
                      .execute()
        return res.data
    except Exception as e:
        print(f"Error al obtener valores de categoría: {e}")
        return []
