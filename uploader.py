#Archivo encargado de hacer la carga (instanciación) de los datos a las tablas de supabase
import os
import pandas as pd
import numpy as np
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import processor
from postgrest import APIError

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def sanitize_df(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        .replace([np.inf, -np.inf], None)
        .where(pd.notnull(df), None)
    )

def cargar_data (df, nombre_tabla, cols_conflicto):
    df_clean = sanitize_df(df)
    records = df_clean.to_dict(orient="records")
    try:
        # dispara APIError si hay un fallo
        response = (
            supabase
            .table(nombre_tabla)
            .upsert(records, on_conflict=",".join(cols_conflicto))
            .execute()
        )

        print(f"{len(records)} filas cargadas en `{nombre_tabla}`")

    except APIError as e:
        # inspecciona el status y contenido crudo
        resp = e.response
        print(f"Error subiendo a `{nombre_tabla}`:")
        print("  HTTP status:", getattr(resp, "status_code", resp.status))
        print("  body:", resp.text)
        raise

def seed_prefijo():
    print('cargando dimension Prefijo en supabase')
    df = processor.poblar_prefijo()
    cargar_data(df, "Prefijo", ["id"])

def exportar_csv (df,nombreArchivo, carpeta: str = "data\processed"):
    if not nombreArchivo.lower().endswith(".csv"):
        nombreArchivo += ".csv"
    
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombreArchivo)
    
    df.to_csv(ruta, index=False, encoding="utf-8")
    
    print(f"CSV {nombreArchivo} exportado en: {ruta}")
    return ruta