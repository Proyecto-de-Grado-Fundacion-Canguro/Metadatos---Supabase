#Archivo donde corre todo el proceso de transformación y carga 
# test_processor.py

from processor import inicializar_dataframes, inicializar_dimensiones, poblar_prefijo


def main():
    print("→ Probando inicializar_dataframes()")
    inicializar_dataframes()

    print("→ Probando poblar_prefijo()")
    # Asegúrate de que df_prefijos ya esté cargado
    poblar_prefijo()


if __name__ == "__main__":
    main()
