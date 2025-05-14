set -e

if [ ! -d "venv" ]; then
  python -m venv venv
  echo "Entorno virtual creado."
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Dependencias instaladas en venv."
