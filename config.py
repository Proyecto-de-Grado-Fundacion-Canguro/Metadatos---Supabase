import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL   = os.getenv("SUPABASE_URL")
SUPABASE_KEY   = os.getenv("SUPABASE_KEY")
DICT_PATH     = "data/raw/KMC-70K-diccionarioVARS-JTH-PhETI-rev20250511.xlsx"
LONG_PATH   = "data/raw/KMC-varLongitudinal.xlsx"
PROCESSED_DIR  = "data/processed"
