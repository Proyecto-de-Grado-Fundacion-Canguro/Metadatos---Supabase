#Transforma los datos en un csv - cada csv es una dimensión
import os, pandas as pd
from config import DICT_PATH, PROCESSED_DIR, LONG_PATH
import uuid




def inicializar_dataframes ():
    """    Inicializa los dataframes del diccionario para poder cargar la información de las dimensiones
    """
    global df_variables, df_fases, df_episodios, df_temasInteres,df_prefijos,df_vLongitudinales,df_categorias,cols_cat
    
    file_dict=pd.ExcelFile(DICT_PATH)
    df_variables=pd.read_excel(file_dict, sheet_name='VARS-(KMC70k)')
    print(df_variables)
    df_fases=pd.read_excel(file_dict, sheet_name='Phases')
    df_episodios=pd.read_excel(file_dict, sheet_name='Episodes')
    df_temasInteres=pd.read_excel(file_dict, sheet_name='TopicsOfInterest')
    df_prefijos=pd.read_excel(file_dict, sheet_name='PREFIX-VARIABLES')

    file_vls=pd.ExcelFile(LONG_PATH)
    df_vLongitudinales=pd.read_excel(file_vls, sheet_name='VLs-Definition')
    df_vLongitudinales.rename(columns={'Unnamed: 0': 'descripcion'}, inplace=True)

    cols_cat = [
    "VAL1", "SHORT-NAME1", "VAL2", "SHORT-NAME2",
    "VAL3", "SHORT-NAME3", "VAL4", "SHORT-NAME4", "VAL5", "SHORT-NAME5",
    "VAL6", "SHORT-NAME6", "VAL7", "SHORT-NAME7", "VAL8", "SHORT-NAME8",
    "VAL9", "SHORT-NAME9", "VAL10", "SHORT-NAME10", "VAL11", "SHORT-NAME11"
    ] 
    df_categorias=df_variables[cols_cat]

    print('inicialización de dataframes exitosa')


def inicializar_dimensiones ():

    # Grupos - Puentes
    grupoOperacion = pd.DataFrame(columns=['id'])
    puenteVariableOperacion = pd.DataFrame(columns=['idVariable','idGrupoOperacion'])
    
    


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
    """
     Encontrar el prefijo de una dimensión y devolver su id
    """
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
    """
    Obtener una lista con todos los episodios posibles de fase y episodio
    """
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
    """
    A partir del nombre de analisis de una variable obtener su id y su descripcion
    """
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
    dia  = date.day
    mes  = date.month
    anio = date.year

    id_str = f"{dia:02d}{mes:02d}{anio}"

    fecha = pd.DataFrame([{
        "id":         id_str,
        "fechaDate":  date,
        "dia":        dia,
        "mes":        mes,
        "anio":       anio
    }])

    return fecha

#### Dimensión Valor Categoria ---------------------------------------------------------------------------------
def crear_diccionario_valor_categoria():
   unique_dicts = set()
   
   for index, row in df_categorias.iterrows():
       for i, col in  enumerate(df_categorias.columns):
            if i + 1 < len(df_categorias.columns):  
                siguiente_col = df_categorias.columns[i + 1]
            if pd.notna(row[col]) and 'VAL' in col and row[col] != ' ':
                dicc={
                'codificacion':int(row[col]),
                'descripcion':str(row[siguiente_col]).strip()
                }
                frozen = frozenset(dicc.items())
                if frozen not in unique_dicts:
                    unique_dicts.add(frozen)
   return unique_dicts

def poblar_valorCategoria():
    unique_dict=crear_diccionario_valor_categoria()
    filas=[]
    for d in unique_dict:
        data=dict(d)
        filas.append({
            'id':str(uuid.uuid4()),
            'codificacion':data['codificacion'],
            'descripcion':data['descripcion']
        })
    valorCategoria = pd.DataFrame(filas,columns=['id','codificacion','descripcion'])
    print(valorCategoria)
    return valorCategoria

#### Dimensión Puente Variable Longitudinal ---------------------------------------------------------------------------------
def poblar_puente_y_grupo_variable_longitudinal(df_variable):
    n = len(df_vLongitudinales)
    ids_grupoVLs = [str(uuid.uuid4()) for _ in range(n)]
    cont=0
    filas=[]
    for index, row in df_vLongitudinales.iterrows():
        for col in df_vLongitudinales.columns:
             if col!='descripcion':
                nombre_variable = row[col]  
                var = df_variable[df_variable['nombreBD'] == nombre_variable]
                if not var.empty:
                    id_variable = var.iloc[0]['id']
                    filas.append({
                        'idGrupoVariable': ids_grupoVLs[cont],
                        'idVariableLongitudinal':id_variable,
                        'descripcion':str(row['descripcion'])+'-'+str(col)
                    })
        cont+=1
    puenteVariableLongitudinal = pd.DataFrame(filas,columns=['idGrupoVariable','idVariableLongitudinal','descripcion'])
    grupoVariableLongitudinal= pd.DataFrame(ids_grupoVLs,columns=['id'])
    return puenteVariableLongitudinal,grupoVariableLongitudinal

#### Dimensión Puente Variable Longitudinal -------------------------------------------------------------------------------
def retornar_valores_categoria_por_variable(row,df_valorcategoria):
    """
    Retorna los ids de la dimensión Valor Categoria para una fila (variable)
    """
    row=row[cols_cat]
    ids=[]
    for i, col in  enumerate(df_categorias.columns):  
        if i + 1 < len(df_categorias.columns):  
             siguiente_col = df_categorias.columns[i + 1]
        if pd.notna(row[col]) and 'VAL' in col and row[col] != ' ':
                val=df_valorcategoria[
                    (df_valorcategoria['codificacion']==row[col]) &
                    (df_valorcategoria['descripcion']==row[siguiente_col])
                ]
                if not val.empty:
                    ids.append(str(val['id'].iloc[0]))
    return ids

#### Dimensión Puente Tema Interes -------------------------------------------------------------------------------
def retornar_temas_interes_por_variable (row,temasInteres):
    cols_tOf=['id-TofI-1','id-TofI-2']
    df_tOf=df_variables[cols_tOf]
    row=row[cols_tOf]
    ids=[]
    for i, col in  enumerate(df_tOf.columns):
        if pd.notna(row[col] and row[col] != ' '):
            mask = (
                temasInteres['nombre']
                .fillna("") 
                .str.replace(r"\s+", "", regex=True)  
                .str.lower()                            
                == 
                str(row[col]).strip().replace(" ", "").lower())
            val = temasInteres[mask]
            if not val.empty:
                    ids.append(str(val['id'].iloc[0]))
    return ids

#### Tabla de hechos Registrar Variable -------------------------------------------------------------------------------
def poblar_tabla_hechos(variable,fase,evento,episodio,temasInteres, puenteVariableLongitudinal,valorCategoria):
   ids_grupoCats = [str(uuid.uuid4()) for _ in range(len(variable))]
   ids_grupoTemas= [str(uuid.uuid4()) for _ in range(len(variable))] 

   grupoTemaInteres = pd.DataFrame(columns=['id'])
   puenteTemaInteres = pd.DataFrame(columns=['idGrupoTemaInteres','idTemaInteres'])

   grupoValorCategoria =pd.DataFrame(columns=['id'])
   puenteCategoria= pd.DataFrame(columns=['idGrupoValorCategoria','idValorCategoria'])

   filas=[]

   for index,row in df_variables.iterrows():
       #id variable
       row_var=variable[variable ['nombreAnalisis']==str(row['ID-VAR'])]
       id_var= str(row_var['id'].iloc[0])

       #id fecha
       id_fecha='01012025'

       #idFase
       row_fase = fase[fase['numFase'] == row['#Phase']]

       if not row_fase.empty:
            # Si hay coincidencia, obtener id_fase
            id_fase = row_fase.iloc[0]['id']

            # Buscar evento inicio fase
            row_evento = df_fases[df_fases['Number-Phase'] == row['#Phase']]
            nombre_evento_inicio_fase = row_evento['Evento inicial (id-var)'].iloc[0]
            # Filtrar el evento de inicio fase
            filtered_evento_inicio_fase = evento[evento['nombre'] == nombre_evento_inicio_fase]

            # Verificar si el filtro devuelve resultados
            if not filtered_evento_inicio_fase.empty:
                id_inicio_fase = filtered_evento_inicio_fase.iloc[0]['id']
            else:
                id_inicio_fase = None  # Asignar None si no se encuentran resultados


            # Buscar evento fin fase
            nombre_evento_fin_fase = row_evento['Evento-final (id-var)'].iloc[0]
            filtered_evento_fin_fase = evento[evento['nombre'] == nombre_evento_fin_fase]

            # Verificar si el filtro devuelve resultados
            if not filtered_evento_fin_fase.empty:
                id_fin_fase = filtered_evento_fin_fase.iloc[0]['id']
            else:
                id_fin_fase = None  # Asignar None si no se encuentran resultados
       else:
            # Si no hay coincidencia, asignar None
            id_fase = None
            id_inicio_fase = None
            id_fin_fase = None

       #id episodio
       row_episodio=episodio[episodio['nombreAnalisis']==row['ID-Episode-1']]
       if not row_episodio.empty:
        # Si hay coincidencia, obtener id_episodio
        id_episodio = row_episodio.iloc[0]['id']

        # Buscar evento inicio episodio
        row_evento_episodio = df_episodios[df_episodios['Number-Episode'] == row['#Episode-1']]
        nombre_evento_inicio_episodio = row_evento_episodio['Evento inicial (id-var)'].iloc[0]

        if isinstance(nombre_evento_inicio_episodio, str):
            nombre_evento_inicio_episodio = nombre_evento_inicio_episodio.strip().lower()
        else:
            nombre_evento_inicio_episodio = ""  # Asigna cadena vacía si no es un string

    
        evento['nombre'] = evento['nombre'].fillna('').str.strip().str.lower()


        if nombre_evento_inicio_episodio:  # Verifica que no esté vacío
            id_inicio_episodio = evento[evento['nombre'] == nombre_evento_inicio_episodio].iloc[0]['id']
        else:
            id_inicio_episodio = None

        # Buscar evento fin episodio
        nombre_evento_fin_episodio = row_evento_episodio['Evento-final (id-var)'].iloc[0]


        if isinstance(nombre_evento_fin_episodio, str):
            nombre_evento_fin_episodio = nombre_evento_fin_episodio.strip().lower()
        else:
            nombre_evento_fin_episodio = ""  


        if nombre_evento_fin_episodio:  
            id_evento_fin_episodio = evento[evento['nombre'] == nombre_evento_fin_episodio].iloc[0]['id']
        else:
            id_evento_fin_episodio = None
       else:
            # Si no hay coincidencia, asignar None
            id_episodio = None
            id_inicio_episodio = None
            id_evento_fin_episodio = None

       #id grupo tema interes
       ids_tOf=retornar_temas_interes_por_variable(row,temasInteres)
       grupo_tOf=ids_grupoTemas[index] #id grupo tema de interes
       
       for tOf in ids_tOf: #poblar grupo tema de interes
           puenteTemaInteres.loc[len(puenteTemaInteres)]=(
               grupo_tOf,
               tOf
           )

       grupoTemaInteres.loc[len(grupoTemaInteres)]=( #poblar grupo tema interes
           grupo_tOf
       )
        
       #id grupo variable longitudinal
       row_vl=puenteVariableLongitudinal[puenteVariableLongitudinal['idVariableLongitudinal']==id_var]
       if not row_vl.empty:
           id_longitudinal= row_vl.iloc[0]['idGrupoVariable']
       else:
           id_longitudinal=None

       #id grupo categoria
       ids_cats=retornar_valores_categoria_por_variable(row,valorCategoria)  
       grupo_cats=ids_grupoCats[index]
       for cats in ids_cats:
           puenteCategoria.loc[len(puenteCategoria)]=(
               grupo_cats,
               cats
           )

       grupoValorCategoria.loc[len(grupoValorCategoria)]=(grupo_cats) #poblar grupo valor categoria

       id_grupo_operacion_null=None

       filas.append({
           'idVariable':id_var,
           'idFechaRegistro': id_fecha,
           'idFase':id_fase,
           'idInicioFase':id_inicio_fase,
           'idFinFase':id_fin_fase,
           'idEpisodio':id_episodio,
           'idInicioEpisodio':id_inicio_episodio,
           'idFinEpisodio':id_evento_fin_episodio,
           'idGrupoTemaInteres':grupo_tOf,
           'idGrupoVariableLongitudinal':id_longitudinal,
           'idGrupoCategoria':grupo_cats,
           'idGrupoOperacion':id_grupo_operacion_null
       })

   hechoRegistrarVariable = pd.DataFrame (filas,columns=['idVariable', 'idFechaRegistro','idFase','idInicioFase','idFinFase','idEpisodio',
                                                    'idInicioEpisodio','idFinEpisodio','idGrupoTemaInteres',
                                                    'idGrupoVariableLongitudinal',
                                                    'idGrupoCategoria','idGrupoOperacion'])
   return hechoRegistrarVariable