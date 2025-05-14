
set -e

if [ -f .env ]; then
  source .env
else
  echo "No se encontró el archivo .env"
  exit 1
fi

#Ejecuta el pipeline completo
python main.py
