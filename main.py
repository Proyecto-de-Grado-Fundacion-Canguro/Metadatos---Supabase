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

if __name__ == "__main__":
    main()
