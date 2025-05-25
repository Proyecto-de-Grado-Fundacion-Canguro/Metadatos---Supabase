import os
import src.processor as processor
import src.supabase_manager as manager
from src.processor import *
from  src.config import DICT_PATH, LONG_PATH


def seed_prefijo():
    print('cargando dimension Prefijo en supabase')
    df = processor.poblar_prefijo()
    manager.cargar_data(df, "Prefijo", ["id"])

def exportar_csv (df,nombreArchivo, carpeta: str = "data\processed"):
    if not nombreArchivo.lower().endswith(".csv"):
        nombreArchivo += ".csv"
    
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombreArchivo)
    
    df.to_csv(ruta, index=False, encoding="utf-8")
    
    print(f"CSV {nombreArchivo} exportado en: {ruta}")
    return ruta



def charge_all_csv():
    inicializar_dataframes()

    df_prefix = poblar_prefijo()
    exportar_csv(df_prefix, "prefijo")
    manager.cargar_data(df_prefix, "prefijo", ["id"])

    df_ti = poblar_temaInteres()
    exportar_csv(df_ti, "tema_interes")
    manager.cargar_data(df_ti, "tema_interes", ["id"])

    df_fase = poblar_fase()
    exportar_csv(df_fase, "fase")
    manager.cargar_data(df_fase, "fase", ["id"])

    df_var = poblar_variable(df_prefix)
    exportar_csv(df_var, "variable")
    manager.cargar_data(df_var, "variable", ["id"])

    df_evento = poblar_evento(df_var)
    exportar_csv(df_evento, "evento")
    manager.cargar_data(df_evento, "evento", ["id"])

    df_episodio = poblar_episodio(df_evento)
    exportar_csv(df_episodio, "episodio")
    manager.cargar_data(df_episodio, "episodio", ["id"])

    df_fecha = poblar_fecha()
    exportar_csv(df_fecha, "fecha")
    manager.cargar_data(df_fecha, "fecha", ["id"])

    df_valor_categoria = poblar_valorCategoria()
    exportar_csv(df_valor_categoria, "valor_categoria")
    manager.cargar_data(df_valor_categoria, "valor_categoria", ["id"])

    puente_vls, grupo_vls = poblar_puente_y_grupo_variable_longitudinal(df_var)
    exportar_csv(grupo_vls, "grupo_variable_longitudinal")
    manager.cargar_data(grupo_vls, "grupo_variable_longitudinal", ["id"])

    exportar_csv(puente_vls, "puente_variable_longitudinal")
    manager.cargar_data(puente_vls, "puente_variable_longitudinal", ["id_grupo_variable", "id_variable_longitudinal"])

    # Poblar hechos y todos los puentes/grupos relacionados
    tabla_hechos, puente_categoria, grupo_valor_categoria, puente_tema_interes, grupo_tema_interes, puente_episodio, grupo_episodio = poblar_tabla_hechos(
        df_var, df_fase, df_evento, df_episodio, df_ti,
        puente_vls, df_valor_categoria
    )

    # Cargar grupo y puente valor categoría
    exportar_csv(grupo_valor_categoria, "grupo_valor_categoria")
    manager.cargar_data(grupo_valor_categoria, "grupo_valor_categoria", ["id"])

    exportar_csv(puente_categoria, "puente_categoria")
    manager.cargar_data(puente_categoria, "puente_categoria", ["id_grupo_valor_categoria", "id_valor_categoria"])

    # Cargar grupo y puente tema interés
    exportar_csv(grupo_tema_interes, "grupo_tema_interes")
    manager.cargar_data(grupo_tema_interes, "grupo_tema_interes", ["id"])

    df_puente_tema_interes = puente_tema_interes.drop_duplicates(subset=["id_grupo_tema_interes", "id_tema_interes"])
    exportar_csv(df_puente_tema_interes, "puente_tema_interes")
    manager.cargar_data(df_puente_tema_interes, "puente_tema_interes", ["id_grupo_tema_interes", "id_tema_interes"])

    # Cargar grupo y puente episodio
    exportar_csv(grupo_episodio, "grupo_episodio")
    manager.cargar_data(grupo_episodio, "grupo_episodio", ["id"])

    exportar_csv(puente_episodio, "puente_episodio")
    manager.cargar_data(puente_episodio, "puente_episodio", ["id_grupo_episodio", "id_episodio"])

    # Cargar tabla de hechos
    exportar_csv(tabla_hechos, "hecho_registrar_variable")
    manager.cargar_data(tabla_hechos, "hecho_registrar_variable", ["id_variable"])
