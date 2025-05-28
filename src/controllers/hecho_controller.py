import math
import src.config as config
import pandas as pd
from src.supabase_manager import supabase
from datetime import date
from src.controllers.controller_general import *
from src.controllers.variable_controller import *
from src.controllers.fase_controller import buscar_fase_por_nombre_bd, obtener_eventos_por_fase
from src.controllers.episodio_controller import *

def limpiar_dict_de_valores_invalidos(dic):
    for k, v in dic.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            dic[k] = None
    return dic

def cargar_hecho():
    df_var = pd.read_excel(config.VARIABLE_FILE)
    for _, row in df_var.iterrows():
        sigla = pd.Series(row['ID-VAR']).str.extract(r'^([^_]+)').iloc[0, 0]
        prefix = obtener_prefijo_por_sigla(sigla)
        print(prefix)

        vars = {
            'nombre_bd': row['NOMBRE EN LA BdeD'],
            'nombre_analisis': row['ID-VAR'],
            'descripcion_corta': row['VAR-SHORT DESCRIPTION'],
            'descripcion_larga': row['VAR-LONG DESCRIPTION'],
            'unidades': row['UNITS'],
            'tipo_dato': row['VAR-TYPE-prim'],
            'nivel_medicion': row['VAR-TYPE-sec'],
            'basica': True,
            'longitudinal': False,
            'derivada': False,
            'impacto': False,
            'id_prefijo': prefix['id']
        }

        id_fase = inicio_fase = fin_fase = None
        if pd.notnull(row.get('ID-Phase')) and row['ID-Phase'].strip():
            fase = buscar_fase_por_nombre_bd(row['ID-Phase'])
            if isinstance(fase, dict) and 'id' in fase:
                id_fase = fase['id']
                eventos_fase = obtener_eventos_por_fase(id_fase)
                if eventos_fase and 'id_evento_inicio' in eventos_fase and 'id_evento_fin' in eventos_fase:
                    inicio_fase = eventos_fase['id_evento_inicio']
                    fin_fase = eventos_fase['id_evento_fin']
                else:
                    print(f" No se encontraron eventos para la fase {id_fase}")
            else:
                print(f" No se encontró la fase con nombre {row['ID-Phase']}")

        episodios = []
        for key in ['ID-Episode-1', 'ID-Episode-2', 'ID-Episode-3']:
            nombre = row.get(key)
            if pd.notnull(nombre) and str(nombre).strip():
                episodio = buscar_episodio_por_nombre(nombre)
                if episodio:
                    episodios.append(episodio)

        ids_episodios = [e['id'] for e in episodios]
        id_grupo_episodios = None
        if ids_episodios:
            resultado_epi = crear_grupo_y_puentes_para_episodios(ids_episodios)
            if isinstance(resultado_epi, dict) and resultado_epi.get('ok') and 'id_grupo' in resultado_epi:
                id_grupo_episodios = resultado_epi['id_grupo']
            else:
                print(f"Error creando grupo de episodios: {resultado_epi}")

        tOf = []
        for key in ['id-TofI-1', 'id-TofI-2']:
            nombre = row.get(key)
            if pd.notnull(nombre) and str(nombre).strip():
                tema = buscar_tema_interes_por_nombre(nombre)
                if tema:
                    tOf.append(tema)

        ids_tOf = [t['id'] for t in tOf]
        id_grupo_tOf = None
        if ids_tOf:
            resultado_tema = crear_grupo_tema_interes_con_temas(ids_tOf)
            if isinstance(resultado_tema, dict) and resultado_tema.get('ok') and 'id_grupo' in resultado_tema:
                id_grupo_tOf = resultado_tema['id_grupo']
            else:
                print(f"Error creando grupo de temas de interés: {resultado_tema}")

        ids_valor_categoria = []
        for i in range(1, 12):
            val = row.get(f"VAL{i}")
            descripcion = row.get(f"SHORT-NAME{i}")
            if pd.notnull(val) and pd.notnull(descripcion):
                try:
                    val_int = int(float(val))
                except ValueError:
                    print(f"Valor no convertible a entero: {val} en VAL{i}")
                    continue

                resultado = agregar_valor_categoria(val_int, str(descripcion))
                if isinstance(resultado, dict) and resultado.get("ok") and "id" in resultado:
                    ids_valor_categoria.append(resultado["id"])
                else:
                    print(f"Error al agregar valor de categoría VAL{i}: {resultado}")

        id_grupo_codificacion = None
        if ids_valor_categoria:
            resultado_cod = crear_grupo_valor_categoria_con_valores(ids_valor_categoria)
            if isinstance(resultado_cod, dict):
                if resultado_cod.get("ok") and "id_grupo" in resultado_cod:
                    id_grupo_codificacion = resultado_cod["id_grupo"]
                else:
                    print(f"Error creando grupo codificación: {resultado_cod}")
            elif isinstance(resultado_cod, str):
                id_grupo_codificacion = resultado_cod 

        id_fecha = crear_fecha_hoy()
        if isinstance(id_fecha, dict):
            if id_fecha.get("ok") and "id" in id_fecha:
                id_fecha = id_fecha["id"]
            else:
                print(f" Error creando fecha: {id_fecha}")
                id_fecha = None

        valor_min = row['VAR-MIN-VALUE']
        valor_max = row['VAR-MAX-VALUE']
        valor_no_conocido = row['VAR-MISSING-VALUE']

        vars = limpiar_dict_de_valores_invalidos(vars)
        variable = crear_variable(vars)
        if not isinstance(variable, dict) or not variable.get('ok') or 'id' not in variable:
            print(f"No se pudo crear variable: {variable}")
            continue

        var_id = variable['id']

        data = {
            "id_variable": var_id,
            "id_fecha_registro": id_fecha,
            "id_fase": id_fase,
            "id_inicio_fase": inicio_fase,
            "id_fin_fase": fin_fase,
            "id_grupo_episodio": id_grupo_episodios,
            "id_grupo_tema_interes": id_grupo_tOf,
            "id_grupo_variable_longitudinal": None,
            "id_grupo_categoria": id_grupo_codificacion,
            "id_grupo_operacion": None,
            "valor_min": valor_min,
            "valor_max": valor_max,
            "valor_no_conocido": valor_no_conocido
        }

        data = limpiar_dict_de_valores_invalidos(data)
        for k in data:
            if isinstance(data[k], dict):
                print(f"Campo {k} tiene dict en lugar de UUID: {data[k]}")
                data[k] = None

        try:
            print("Insertando hecho...")
            supabase.table("hecho_registrar_variable").insert(data).execute()
            print({"ok": True, "msg": "Registro insertado correctamente en hecho_registrar_variable"})
        except Exception as e:
            print({"ok": False, "msg": f"Error al insertar hecho: {str(e)}"})
