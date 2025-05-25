#Archivo donde corre todo el proceso de transformación y carga 
from processor import *
from uploader import *
from supabase_manager import *


def main():
    charge_all_csv()

if __name__ == "__main__":
    main()
