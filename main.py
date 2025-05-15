#Archivo donde corre todo el proceso de transformación y carga 
from processor import *
from uploader import *


def main():
    print("→ Probando inicializar_dataframes()")
    inicializar_dataframes()

    print("→ Probando poblar_fase()")
    # Asegúrate de que df_prefijos ya esté cargado
    df_prefijo=poblar_prefijo()
    df_var=poblar_variable(df_prefijo)
    poblar_evento(df_var)


if __name__ == "__main__":
    main()
