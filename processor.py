#Transforma los datos en un csv - cada csv es una dimensión
import os, pandas as pd
from config import DICT_PATH, PROCESSED_DIR, LONG_PATH
import uuid



# Inicializar dataframes según el diccionario de variables 
def inicializar_dataframes ():
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

    episodio = pd.DataFrame(columns=['id','nombre','descripcion','fechaInicio','fechaFin','activo'])
    evento = pd.DataFrame(columns=['id','nombre','fecha','descripcion','fechaInicio','fechaFin','activo'])
    fase = pd.DataFrame(columns=['id','numFase','nombreAnalisis','nombreBD','descripcion','ultimo','fechaInicio','fechaFin','activo'])
    fecha= pd.DataFrame(columns=['id','fechaDate','dia','mes','anio'])
    variable= pd.DataFrame(columns=['id','nombreBD','nombreAnalisis','descripcionCorta','descripcionLarga','unidades','tipoDato',
                                    'tipoVariable','nivelMedicion','basica','derivada','variableObjetivo','edadCorregida','impacto','idPrefijo'])

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
    

def poblar_prefijo():
    global prefijo
    filas = []
    for _, row in df_prefijos.iterrows():
        filas.append({
            "id": str(uuid.uuid4()),
            "sigla": row["SIGLA"],
            "descripcion": row["DESCRIPCION"]
        })
    prefijo = pd.DataFrame(filas, columns=["id", "sigla", "descripcion"])
    return prefijo

    