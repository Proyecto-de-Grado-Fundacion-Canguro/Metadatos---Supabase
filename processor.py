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
    return variable


def encontrar_prefijo_por_sigla(sigla: str, prefijo_df: pd.DataFrame) -> str | None:
    sigla_upper = sigla.upper()
    mask = prefijo_df["sigla"].fillna("").str.upper() == sigla_upper
    matches = prefijo_df[mask]
    if matches.empty:
        return None
    return matches.iloc[0]["id"]

#### Dimensión Evento ---------------------------------------------------------------------------------
def poblar_evento(variable_df):
    filas=[]
    inicio_anio = pd.Timestamp(year=2025, month=1, day=1)
    fin_anio    = pd.Timestamp(year=9999, month=12, day=31)
    evs=obtener_lista_episodios()
    print('1111111111111111111')
    print(evs)
    for ev in evs:
        info=obtener_info_variable(variable_df,ev)
        if info is None:
            id_var, desc_corta = None, ""
        else:
            id_var, desc_corta = info

        filas.append({
            "id":               str(uuid.uuid4()),
            "nombre":           ev,
            "idVariableFecha":       id_var,
            "descripcion": desc_corta,
            "fechaInicio":      inicio_anio,
            "fechaFin":         fin_anio,
            "activo":           True

        })
    
    evento = pd.DataFrame(filas,columns=['id','nombre','idVariableFecha','descripcion','fechaInicio','fechaFin','activo']) 
    print(evento)
    return evento

def obtener_lista_episodios():
    eventos_fases=(
        pd.concat([
            df_fases['Evento inicial (id-var)'],
            df_fases['Evento-final (id-var)']
        ])
    .dropna()              
    .drop_duplicates()     
    .tolist()
    )

    eventos_episodios=(
        pd.concat([
            df_episodios['Evento inicial (id-var)'],
            df_episodios['Evento-final (id-var)']
        ])
    .dropna()             
    .drop_duplicates()     
    .tolist()
    )

    eventos_union = (
    pd.Series(eventos_fases + eventos_episodios)
      .drop_duplicates()
      .tolist()
    )
    return eventos_union


def obtener_info_variable (variable_df,nombreAnalisis):
    var=variable_df[variable_df['nombreAnalisis']==nombreAnalisis]
    if var.empty:
        return None
    fila = var.iloc[0]
    id_val      = fila['id']
    desc_corta  = fila['descripcionCorta']
    
    return [id_val, desc_corta]

#### Dimensión Fecha ---------------------------------------------------------------------------------

def poblar_fecha (inicio: str = "2025-01-01"):
    date = pd.to_datetime(inicio).date()
    dia  = fecha.day
    mes  = fecha.month
    anio = fecha.year

    id_str = f"{dia:02d}{mes:02d}{anio}"

    fecha = pd.DataFrame([{
        "id":         id_str,
        "fechaDate":  date,
        "dia":        dia,
        "mes":        mes,
        "anio":       anio
    }])

    return fecha