import sys
import os
from datetime import datetime
from postgrest import APIError
from supabase import create_client
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from supabase import create_client
from src.config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#---------------Cargar dataframes a Supabase------------
def cargar_data(df, nombre_tabla, cols_conflicto):
    

    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)

    def safe_convert(value):
        if isinstance(value, (pd.Timestamp, datetime.datetime, datetime.date)):
            return value.strftime('%Y-%m-%d')
        elif pd.isna(value):
            return None
        return value

    records = df.applymap(safe_convert).to_dict(orient="records")

    try:
        response = (
            supabase
            .table(nombre_tabla)
            .upsert(records, on_conflict=",".join(cols_conflicto))
            .execute()
        )
        print(f"{len(records)} filas cargadas en `{nombre_tabla}`")

    except APIError as e:
        print("Error de Supabase:")
        print(e)
        print(getattr(e, 'args', None))


