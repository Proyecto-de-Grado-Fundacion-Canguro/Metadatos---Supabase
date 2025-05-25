from supabase import create_client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY
from postgrest import APIError

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cargar_data(df, nombre_tabla, cols_conflicto):
    import numpy as np
    import pandas as pd
    import datetime

    # Reemplazar infinitos y NaN por None
    df = df.replace([np.inf, -np.inf], None)
    df = df.where(pd.notnull(df), None)

    # Convertir datetime, Timestamp y NaT a string ISO 8601
    def safe_convert(value):
        if isinstance(value, (pd.Timestamp, datetime.datetime, datetime.date)):
            return value.strftime('%Y-%m-%d')
        elif pd.isna(value):
            return None
        return value

    # Convertir todos los valores del DataFrame
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

