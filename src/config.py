import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL   = os.getenv("SUPABASE_URL")
SUPABASE_KEY   = os.getenv("SUPABASE_KEY")
DICT_PATH     = "data/raw/KMC-70K-diccionarioVARS-JTH-PhETI-rev20250520.xlsx"
LONG_PATH   = "data/raw/KMC-70k-VarLongitudinal.xlsx"
PROCESSED_DIR  = "data/processed"
VARIABLE_FILE=""

def set_dict_paths(ruta_diccionario, ruta_vls):
    global DICT_PATH, LONG_PATH
    DICT_PATH = ruta_diccionario
    LONG_PATH=ruta_vls

def set_variable_path(ruta):
    global VARIABLE_FILE
    VARIABLE_FILE=ruta
