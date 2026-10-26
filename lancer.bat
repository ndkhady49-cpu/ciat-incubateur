@echo off
cd /d "%~dp0"
if not exist .venv ( python -m venv .venv )
call .venv\Scripts\activate
pip install -q -r requirements.txt
python manage.py makemigrations incubateur
python manage.py migrate
python manage.py seed
echo.
echo Ouvrez http://127.0.0.1:8000 dans votre navigateur
python manage.py runserver
pause
