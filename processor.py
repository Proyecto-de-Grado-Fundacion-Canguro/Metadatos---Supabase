#Transforma los datos en un csv - cada csv es una dimensión
import os, pandas as pd
from config import DICT_PATH, PROCESSED_DIR, LONG_PATH
import uuid



# Inicializar dataframes según el diccionario de variables 
def inicializar_dataframes ():
    """
    Inicializa los dataframes básicos para poder cargar la información de las dimensiones
    """
    global df_variables, df_fases, df_episodios, df_temasInteres,df_prefijos
    
    file_dict=pd.ExcelFile(DICT_PATH)
    df_variables=pd.read_excel(file_dict, sheet_name='VARS-(KMC70k)')
    print(df_variables)
    df_fases=pd.read_excel(file_dict, sheet_name='Phases')
    df_episodios=pd.read_excel(file_dict, sheet_name='Episodes')
    df_temasInteres=pd.read_excel(file_dict, sheet_name='TopicsOfInterest')
    df_prefijos=pd.read_excel(file_dict, sheet_name='PREFIX-VARIABLES')

    print('inicialización de dataframes exitosa')

# Inicializar dimensiones según sus atributos
def inicializar_dimensiones ():
    global episodio,evento,fase,fecha, grupoOperacion,grupoTemaInteres,grupoValorCategoria,grupoVariableLongitudinal
    global puenteTemaInteres,puenteCategoria,puenteVariableLongitudinal, variable, puenteVariableOperacion, valorCategoria, temaInteres
    global hechoRegistrarVariable

    
    evento = pd.DataFrame(columns=['id','nombre','fecha','descripcion','fechaInicio','fechaFin','activo'])
   
    fecha= pd.DataFrame(columns=['id','fechaDate','dia','mes','anio'])
    

    # Grupos - Puentes
    grupoOperacion = pd.DataFrame(columns=['id'])
    puenteVariableOperacion = pd.DataFrame(columns=['idVariable','idGrupoOperacion'])

    temaInteres = pd.DataFrame(columns=['id','nombre','descripcion'])
    grupoTemaInteres = pd.DataFrame(columns=['id'])
    puenteTemaInteres = pd.DataFrame(columns=['idGrupoTemaInteres','idTemaInteres'])

    valorCategoria = pd.DataFrame(columns=['id','codificacion','descripcion'])
    grupoValorCategoria =pd.DataFrame(columns=['id'])
    puenteCategoria= pd.DataFrame(columns=['idGrupoValorCategoria','idValorCategoria'])

    grupoVariableLongitudinal= pd.DataFrame(columns=['id'])
    puenteVariableLongitudinal = pd.DataFrame(columns=['idGrupoVariable','idVariableLongitudinal'])

    # Tabla de hechos
    hechoRegistrarVariable = pd.DataFrame (columns=['idVariable', 'idFechaRegistro','idFase','idInicioFase','idFinFase','idEpisodio',
                                                    'idInicioEpisodio','idFinEpisodio','idGrupoTemaInteres','idGreupoVariableLongitudinal',
                                                    'idGrupoCategoria','idGrupoOperacion'])
    

#### Dimensión Prefijo ---------------------------------------------------------------------------------
def poblar_prefijo():
    filas = []
    for _, row in df_prefijos.iterrows():
        filas.append({
            "id": str(uuid.uuid4()),
            "sigla": row["SIGLA"],
            "descripcion": row["DESCRIPCION"]
        })
    prefijo = pd.DataFrame(filas, columns=["id", "sigla", "descripcion"])
    return prefijo

#### Dimensión Tema de Interes ---------------------------------------------------------------------------------
def poblar_temaInteres():
    filas = []
    for _, row in df_temasInteres.iterrows():
        filas.append({
            'id': str(uuid.uuid4()),
            'nombre': row['ID-TdI'],
            'descripcion': row['DescripciOn']
        })
    temaInteres = pd.DataFrame(filas, columns=['id', 'nombre', 'descripcion'])
    return temaInteres

#### Dimensión Fase --------------------------------------------------------------------------------------------------
def poblar_fase():
    filas=[]
    ultimo= False
    inicio_anio = pd.Timestamp(year=2025, month=1, day=1)
    fin_anio    = pd.Timestamp(year=9999, month=12, day=31)
    print(df_fases)
    for i,row in df_fases.iterrows():
        if (i==len(df_fases)-1):
            ultimo= True
        filas.append({
            'id':str(uuid.uuid4()),
            'nombreAnalisis':row['NOMBRE CORTO'],
            'nombreBD':row['ID-Phase'],
            'descripcion':row['DESCRIPCION'],
            'ultimo':ultimo,
            'fechaInicio':inicio_anio,
            'fechaFin': fin_anio,
            'activo':True,
            'numFase':row['Number-Phase']
        })
    fase = pd.DataFrame(filas,columns=['id','nombreAnalisis','nombreBD','descripcion','ultimo','fechaInicio','fechaFin','activo','numFase'])
    return fase

#### Dimensión Episodio ---------------------------------------------------------------------------------
def poblar_episodio():
    filas=[]
    inicio_anio = pd.Timestamp(year=2025, month=1, day=1)
    fin_anio    = pd.Timestamp(year=9999, month=12, day=31)
    for _,row in df_episodios.iterrows():
        filas.append({
            'id':str(uuid.uuid4()),
            'descripcion':row['DESCRIPCION'],
            'fechaInicio':inicio_anio,
            'fechaFin':fin_anio,
            'activo':True,
            'nombreAnalisis':row['ID-Episode'],
            'nombreBD':row['NOMBRE CORTO']
        })
    episodio = pd.DataFrame(filas,columns=['id','descripcion','fechaInicio','fechaFin','activo','nombreAnalisis','nombreBD'])
    print(episodio)
    return episodio

#### Dimensión Variable ---------------------------------------------------------------------------------
def poblar_variable(df_prefijo):
    filas=[]
    for _,row in df_variables.iterrows():
        raw = row["ID-VAR"]
        raw_str = str(raw)
        sigla=raw_str.split("_", 1)[0]
        prefix=encontrar_prefijo_por_sigla(sigla,df_prefijo)
        filas.append({
            'id':str(uuid.uuid4()),
            'nombreBD':row['NOMBRE EN LA BdeD'],
            'nombreAnalisis':row['ID-VAR'],
            'descripcionCorta':row['VAR-SHORT DESCRIPTION'],
            'descripcionLarga':row['VAR-LONG DESCRIPTION'],
            'unidades':row['UNITS'],
            'tipoDato':row['VAR-TYPE'],
            'tipoVariable':'',
            'nivelMedicion':'',
            'basica': True, #TODO: preguntar
            'longitudinal': True, #TODO: cargar de archivo longitudinal
            'derivada': False,
            'variableObjetivo': False, 
            'edadCorregida': False,
            'impacto': False,
            'idPrefijo':prefix
        })
    variable= pd.DataFrame(filas,columns=['id','nombreBD','nombreAnalisis','descripcionCorta','descripcionLarga','unidades','tipoDato',
                                    'tipoVariable','nivelMedicion','basica','longitudinal','derivada','variableObjetivo','edadCorregida','impacto','idPrefijo'])
    print(variable)
    return variable


def encontrar_prefijo_por_sigla(sigla: str, prefijo_df: pd.DataFrame) -> str | None:
    sigla_upper = sigla.upper()
    mask = prefijo_df["sigla"].fillna("").str.upper() == sigla_upper
    matches = prefijo_df[mask]
    if matches.empty:
        return None
    return matches.iloc[0]["id"]

#### Dimensión Evento ---------------------------------------------------------------------------------
def poblar_evento():
    filas=[]