#!/bin/sh
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
python manage.py makemigrations incubateur
python manage.py migrate
python manage.py seed
echo "Ouvrez http://127.0.0.1:8000 dans votre navigateur"
python manage.py runserver
