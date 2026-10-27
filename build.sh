#!/usr/bin/env bash
# Build Render : dépendances, fichiers statiques, migrations, compte coordonnateur et démonstration :
# SEED_DEMO=1 crée les comptes de démonstration (une seule fois), SEED_DEMO=supprimer les retire.
# Les migrations sont générées en local (makemigrations) et versionnées : jamais en production.
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py init_coordo
case "$SEED_DEMO" in
  1) python manage.py seed ;;
  supprimer) python manage.py seed --supprimer ;;
esac
