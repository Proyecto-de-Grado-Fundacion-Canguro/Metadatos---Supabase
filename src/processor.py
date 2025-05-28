#Transforma los datos en un csv - cada csv es una dimensión
import pandas as pd
from src.config import DICT_PATH, LONG_PATH
import uuid


def inicializar_dataframes ():
    """    Inicializa los dataframes del diccionario para poder cargar la información de las dimensiones
    """
    global df_variables, df_fases, df_episodios, df_temasInteres,df_prefijos,df_vLongitudinales,df_categorias,cols_cat
    
    file_dict=pd.ExcelFile(DICT_PATH)
    df_variables=pd.read_excel(file_dict, sheet_name='VARS-(KMC70k)')
    df_fases=pd.read_excel(file_dict, sheet_name='Phases')
    df_episodios=pd.read_excel(file_dict, sheet_name='Episodes')
    df_temasInteres=pd.read_excel(file_dict, sheet_name='TopicsOfInterest')
    df_prefijos=pd.read_excel(file_dict, sheet_name='PREFIX-VARIABLES')

    file_vls=pd.ExcelFile(LONG_PATH)
    df_vLongitudinales=pd.read_excel(file_vls, sheet_name='VLs-Definition')

    cols_cat = [
    "VAL1", "SHORT-NAME1", "VAL2", "SHORT-NAME2",
    "VAL3", "SHORT-NAME3", "VAL4", "SHORT-NAME4", "VAL5", "SHORT-NAME5",
    "VAL6", "SHORT-NAME6", "VAL7", "SHORT-NAME7", "VAL8", "SHORT-NAME8",
    "VAL9", "SHORT-NAME9", "VAL10", "SHORT-NAME10", "VAL11", "SHORT-NAME11"
    ] 
    df_categorias=df_variables[cols_cat]

    print('inicialización de dataframes exitosa')
    

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
            'id': str(uuid.uuid4()),
            'nombre_analisis': row['NOMBRE CORTO'],
            'nombre_bd': row['ID-Phase'],
            'descripcion': row['DESCRIPCION'],
            'ultimo': ultimo,
            'fecha_inicio': inicio_anio,
            'fecha_fin': fin_anio,
            'activo': True,
            'num_fase': row['Number-Phase']
        })
    fase = pd.DataFrame(filas,columns=['id','nombre_analisis','nombre_bd','descripcion','ultimo','fecha_inicio','fecha_fin','activo','num_fase'])
    return fase

def poblar_fase_evento(evento_df, fase_df):
    filas = []
    # Creamos un diccionario para acceder rápido al ID de un evento por su nombre
    evento_dict = dict(zip(evento_df['nombre'], evento_df['id']))

    for i, row in df_fases.iterrows():
        nombre_bd_fase = row['ID-Phase']

        # Buscamos el id de la fase en fase_df usando el nombre_bd
        id_fase = fase_df.loc[fase_df['nombre_bd'] == nombre_bd_fase, 'id'].values
        if len(id_fase) == 0:
            continue  # Saltamos si no se encuentra la fase
        id_fase = id_fase[0]

        nombre_evento_inicio = row['Evento inicial (id-var)']
        nombre_evento_fin = row['Evento-final (id-var)']

        id_evento_inicio = evento_dict.get(nombre_evento_inicio)
        id_evento_fin = evento_dict.get(nombre_evento_fin)

        if id_evento_inicio and id_evento_fin:
            filas.append({
                'id_fase': id_fase,
                'id_evento_inicio': id_evento_inicio,
                'id_evento_fin': id_evento_fin
            })

    fase_evento_df = pd.DataFrame(filas, columns=['id_fase', 'id_evento_inicio', 'id_evento_fin'])
    return fase_evento_df


#### Dimensión Episodio ---------------------------------------------------------------------------------
def poblar_episodio(evento_df):
    filas = []
    inicio_anio = pd.Timestamp(year=2025, month=1, day=1)
    fin_anio = pd.Timestamp(year=9999, month=12, day=31)

    evento_df['nombre'] = evento_df['nombre'].fillna('').str.strip().str.lower()

    for _, row in df_episodios.iterrows():
        if pd.notna(row['DESCRIPCION']):
            nombre_inicio = str(row['Evento inicial (id-var)']).strip().lower()
            nombre_fin = str(row['Evento-final (id-var)']).strip().lower()

            evento_inicio = evento_df[evento_df['nombre'] == nombre_inicio]
            evento_fin = evento_df[evento_df['nombre'] == nombre_fin]

            id_evento_inicio = evento_inicio.iloc[0]['id'] if not evento_inicio.empty else None
            id_evento_fin = evento_fin.iloc[0]['id'] if not evento_fin.empty else None

            filas.append({
                'id': str(uuid.uuid4()),
                'descripcion': row['DESCRIPCION'].strip(),
                'fecha_inicio': inicio_anio,
                'fecha_fin': fin_anio,
                'activo': True,
                'nombre_analisis': row['ID-Episode'],
                'nombre_bd': row['NOMBRE CORTO'],
                'id_evento_inicio': id_evento_inicio,
                'id_evento_fin': id_evento_fin
            })

    episodio = pd.DataFrame(filas, columns=[
        'id', 'descripcion', 'fecha_inicio', 'fecha_fin', 'activo',
        'nombre_analisis', 'nombre_bd', 'id_evento_inicio', 'id_evento_fin'
    ])
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
            'id': str(uuid.uuid4()),
            'nombre_bd': row['NOMBRE EN LA BdeD'],
            'nombre_analisis': row['ID-VAR'],
            'descripcion_corta': row['VAR-SHORT DESCRIPTION'],
            'descripcion_larga': row['VAR-LONG DESCRIPTION'],
            'unidades': row['UNITS'],
            'tipo_dato': row['VAR-TYPE-prim'],
            'nivel_medicion': row['VAR-TYPE-sec'],
            'basica': True,
            'longitudinal': True,
            'derivada': False,
            'impacto': False,
            'id_prefijo': prefix
        })
    variable= pd.DataFrame(filas,columns=['id','nombre_bd','nombre_analisis','descripcion_corta','descripcion_larga','unidades','tipo_dato',
                                          'nivel_medicion','basica','longitudinal','derivada','impacto','id_prefijo'])
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
            "id": str(uuid.uuid4()),
            "nombre": ev,
            "id_variable_fecha": id_var,
            "descripcion": desc_corta,
            "fecha_inicio": inicio_anio,
            "fecha_fin": fin_anio,
            "activo": True

        })
    
    evento = pd.DataFrame(filas,columns=['id','nombre','id_variable_fecha','descripcion','fecha_inicio','fecha_fin','activo']) 
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
    var=variable_df[variable_df['nombre_analisis']==nombreAnalisis]
    if var.empty:
        return None
    fila = var.iloc[0]
    id_val      = fila['id']
    desc_corta  = fila['descripcion_corta']
    
    return [id_val, desc_corta]

#### Dimensión Fecha ---------------------------------------------------------------------------------
def poblar_fecha (inicio: str = "2025-01-01"):
    date = pd.to_datetime(inicio).date()
    dia  = date.day
    mes  = date.month
    anio = date.year

    id_str = f"{dia:02d}{mes:02d}{anio}"

    fecha = pd.DataFrame([{
        "id": f"{date.day:02d}{date.month:02d}{date.year}",
        "fecha_date": date,
        "dia": date.day,
        "mes": date.month,
        "anio": date.year
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
    return valorCategoria

#### Dimensión Puente Variable Longitudinal ---------------------------------------------------------------------------------
def poblar_puente_y_grupo_variable_longitudinal(df_variable):
    n = len(df_vLongitudinales)
    ids_grupoVLs = [str(uuid.uuid4()) for _ in range(n)]
    filas = []
    filas_grupos = []
    
    for row in range(1, len(df_vLongitudinales)):
        grupo_nombre = df_vLongitudinales.iloc[row, 0]  
        filas_grupos.append({
            'id': ids_grupoVLs[row],
            'nombre': grupo_nombre
        })

        for col in range(1, len(df_vLongitudinales.columns)):
            nombre_variable = df_vLongitudinales.iloc[row, col]
            var = df_variable[df_variable['nombre_bd'] == nombre_variable]

            if not var.empty:
                id_variable = var.iloc[0]['id']
                fase = df_vLongitudinales.columns[col]  
                abcisa = df_vLongitudinales.iloc[0, col]  
                
                descripcion = f"{grupo_nombre} - {fase}"

                filas.append({
                    'id_grupo_variable': ids_grupoVLs[row],
                    'id_variable_longitudinal': id_variable,
                    'descripcion': descripcion,
                    'abcisa': abcisa
                })

                
    puenteVariableLongitudinal = pd.DataFrame(filas,columns=['id_grupo_variable','id_variable_longitudinal','descripcion','abcisa'])
    grupoVariableLongitudinal = pd.DataFrame(filas_grupos, columns=['id','nombre'])
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
def retornar_episodios_por_variable(row, df_episodios):
    cols_epi = ['ID-Episode-1', 'ID-Episode-2','ID-Episode-3']
    ids = []
    for col in cols_epi:
        if pd.notna(row[col]) and row[col] != ' ':
            val = str(row[col]).strip()
            match = df_episodios[df_episodios['nombre_analisis'].fillna('').str.strip() == val]
            if not match.empty:
                ids.append(str(match.iloc[0]['id']))
    return ids

def crear_grupo_y_puente_episodios(index, row, df_episodios, ids_grupo_episodios, puente_episodio, grupo_episodio):
    ids_epi = retornar_episodios_por_variable(row, df_episodios)
    grupo_epi = ids_grupo_episodios[index]
    for epi_id in ids_epi:
        puente_episodio.loc[len(puente_episodio)] = (grupo_epi, epi_id)
    grupo_episodio.loc[len(grupo_episodio)] = (grupo_epi)
    return grupo_epi


def obtener_info_fase(row, fase, evento):
    row_fase = fase[fase['num_fase'] == row['#Phase']]
    if row_fase.empty:
        return None, None, None
    id_fase = row_fase.iloc[0]['id']

    row_evento = df_fases[df_fases['Number-Phase'] == row['#Phase']]
    nombre_evento_inicio_fase = row_evento['Evento inicial (id-var)'].iloc[0] if not row_evento.empty else None
    nombre_evento_fin_fase = row_evento['Evento-final (id-var)'].iloc[0] if not row_evento.empty else None

    evento_inicio = evento[evento['nombre'] == nombre_evento_inicio_fase] if nombre_evento_inicio_fase else pd.DataFrame()
    evento_fin = evento[evento['nombre'] == nombre_evento_fin_fase] if nombre_evento_fin_fase else pd.DataFrame()

    id_inicio = evento_inicio.iloc[0]['id'] if not evento_inicio.empty else None
    id_fin = evento_fin.iloc[0]['id'] if not evento_fin.empty else None
    return id_fase, id_inicio, id_fin


def crear_grupo_y_puente_temas(index, row, temas_interes, ids_grupo_temas, puente_tema_interes, grupo_tema_interes):
    ids_tof = retornar_temas_interes_por_variable(row, temas_interes)
    grupo_tof = ids_grupo_temas[index]
    for tof in ids_tof:
        puente_tema_interes.loc[len(puente_tema_interes)] = (grupo_tof, tof)
    grupo_tema_interes.loc[len(grupo_tema_interes)] = (grupo_tof)
    return grupo_tof

def crear_grupo_y_puente_categorias(index, row, valor_categoria, ids_grupo_cats, puente_categoria, grupo_valor_categoria):
    ids_cats = retornar_valores_categoria_por_variable(row, valor_categoria)
    grupo_cats = ids_grupo_cats[index]
    for cats in ids_cats:
        puente_categoria.loc[len(puente_categoria)] = (grupo_cats, cats)
    grupo_valor_categoria.loc[len(grupo_valor_categoria)] = (grupo_cats)
    return grupo_cats

def crear_fila_hecho(row_var, row, id_fecha, id_fase, id_inicio_fase, id_fin_fase,
                     id_grupo_episodio, id_grupo_tema_interes,
                     id_grupo_variable_longitudinal, id_grupo_categoria):
    return {
        'id_variable': str(row_var.iloc[0]['id']),
        'id_fecha_registro': id_fecha,
        'id_fase': id_fase,
        'id_inicio_fase': id_inicio_fase,
        'id_fin_fase': id_fin_fase,
        'id_grupo_episodio': id_grupo_episodio,
        'id_grupo_tema_interes': id_grupo_tema_interes,
        'id_grupo_variable_longitudinal': id_grupo_variable_longitudinal,
        'id_grupo_categoria': id_grupo_categoria,
        'id_grupo_operacion': None,
        'valor_min': row['VAR-MIN-VALUE'],
        'valor_max': row['VAR-MAX-VALUE'],
        'valor_no_conocido': row['VAR-MISSING-VALUE']
    }


def poblar_tabla_hechos(variable, fase, evento, episodio, temas_interes, puente_variable_longitudinal, valor_categoria):
    ids_grupo_cats = [str(uuid.uuid4()) for _ in range(len(variable))]
    ids_grupo_temas = [str(uuid.uuid4()) for _ in range(len(variable))]
    ids_grupo_episodios = [str(uuid.uuid4()) for _ in range(len(variable))]

    grupo_tema_interes = pd.DataFrame(columns=['id'])
    puente_tema_interes = pd.DataFrame(columns=['id_grupo_tema_interes', 'id_tema_interes'])

    grupo_valor_categoria = pd.DataFrame(columns=['id'])
    puente_categoria = pd.DataFrame(columns=['id_grupo_valor_categoria', 'id_valor_categoria'])

    grupo_episodio = pd.DataFrame(columns=['id'])
    puente_episodio = pd.DataFrame(columns=['id_grupo_episodio', 'id_episodio'])

    filas = []

    for index, row in df_variables.iterrows():
        row_var = variable[variable['nombre_analisis'] == str(row['ID-VAR'])]
        if row_var.empty:
            continue

        id_variable = str(row_var.iloc[0]['id'])
        id_fecha = '01012025'

        id_fase, id_inicio_fase, id_fin_fase = obtener_info_fase(row, fase, evento)
        id_grupo_episodio = crear_grupo_y_puente_episodios(index, row, episodio, ids_grupo_episodios, puente_episodio, grupo_episodio)
        id_grupo_tema_interes = crear_grupo_y_puente_temas(index, row, temas_interes, ids_grupo_temas, puente_tema_interes, grupo_tema_interes)

        row_vl = puente_variable_longitudinal[puente_variable_longitudinal['id_variable_longitudinal'] == id_variable]
        id_grupo_variable_longitudinal = row_vl.iloc[0]['id_grupo_variable'] if not row_vl.empty else None

        id_grupo_categoria = crear_grupo_y_puente_categorias(index, row, valor_categoria, ids_grupo_cats, puente_categoria, grupo_valor_categoria)

        filas.append(crear_fila_hecho(
            row_var, row, id_fecha, id_fase, id_inicio_fase, id_fin_fase,
            id_grupo_episodio, id_grupo_tema_interes,
            id_grupo_variable_longitudinal, id_grupo_categoria
        ))

    hecho_registrar_variable = pd.DataFrame(filas)

    return (
        hecho_registrar_variable,
        puente_categoria, grupo_valor_categoria,
        puente_tema_interes, grupo_tema_interes,
        puente_episodio, grupo_episodio
    )


