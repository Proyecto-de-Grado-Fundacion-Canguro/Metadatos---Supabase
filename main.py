#Archivo donde corre todo el proceso de transformación y carga 
from processor import *
from uploader import *


def main():
    print("→ Probando inicializar_dataframes()")
    inicializar_dataframes()

    print("→ Probando-...")
    
    df_prefix=poblar_prefijo()
    exportar_csv(df_prefix,"prefijo")

    df_ti=poblar_temaInteres()
    exportar_csv(df_ti,"Tema Interes")


    df_fase_load=poblar_fase()
    exportar_csv(df_fase_load,"fase")

    df_episodios_load=poblar_episodio()
    exportar_csv(df_episodios_load,"Episodio")

    df_var=poblar_variable(df_prefix)
    exportar_csv(df_var,"variable")

    df_evento_load=poblar_evento(df_var)
    exportar_csv(df_evento_load,"evento")

    df_fecha=poblar_fecha()
    exportar_csv(df_fecha,"fecha")

    df_valorCategoria=poblar_valorCategoria()
    exportar_csv(df_valorCategoria,'valor categoria')

    puenteVls, grupoVls= poblar_puente_y_grupo_variable_longitudinal(df_var)
    exportar_csv(puenteVls,'puent variable longitudinal')
    exportar_csv(grupoVls, 'grupo variable longitudinal')

    tabla_hechos,puenteCategoria,grupoValorCategoria,puenteTemaInteres,grupoTemaInteres=poblar_tabla_hechos(df_var,df_fase_load,df_evento_load,df_episodios_load,df_ti,
                                     puenteVls,df_valorCategoria)
    exportar_csv(tabla_hechos,'tabla hechos')
    exportar_csv(puenteCategoria,'puente categoria')
    exportar_csv(grupoValorCategoria,'grupoValorCategoria')
    exportar_csv(puenteTemaInteres,'puente tema de interes')
    exportar_csv(grupoTemaInteres,'grupo tema de interes')

if __name__ == "__main__":
    main()
