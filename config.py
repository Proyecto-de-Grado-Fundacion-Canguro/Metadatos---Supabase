import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL   = os.getenv("SUPABASE_URL")
SUPABASE_KEY   = os.getenv("SUPABASE_KEY")
EXCEL_PATH     = "data/raw/diccionario_datos.xlsx"
PROCESSED_DIR  = "data/processed"
