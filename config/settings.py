"""Réglages du projet CIAT Incubateur.
Variables d'environnement (voir LISEZ-MOI) :
- DJANGO_SECRET_KEY (obligatoire en production), DJANGO_DEBUG (1 par défaut, 0 en production),
  DJANGO_ALLOWED_HOSTS et DJANGO_CSRF_ORIGINS (séparés par des virgules)
- DATABASE_URL : base PostgreSQL (Neon). Absente : SQLite locale (db.sqlite3)
- R2_BUCKET, R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY : fichiers sur Cloudflare R2. Absentes : dossier media/
- ANTHROPIC_API_KEY : assistant IA (facultatif)
"""
import logging
import os
import re
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or ("dev-changez-moi-en-production" if DEBUG else "")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY est obligatoire quand DJANGO_DEBUG=0.")
ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "*" if DEBUG else "").split(",") if h]
CSRF_TRUSTED_ORIGINS = [o for o in os.environ.get("DJANGO_CSRF_ORIGINS", "").split(",") if o]

_render = os.environ.get("RENDER_EXTERNAL_HOSTNAME")  # fourni par Render
if _render:
    ALLOWED_HOSTS.append(_render)
    CSRF_TRUSTED_ORIGINS.append("https://" + _render)

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "incubateur",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

# Base de données : PostgreSQL si DATABASE_URL est défini (production), sinon SQLite (développement)
if os.environ.get("DATABASE_URL"):
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, conn_health_checks=True, ssl_require=not DEBUG)}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}

AUTH_USER_MODEL = "incubateur.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "accueil"
LOGOUT_REDIRECT_URL = "login"
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Dakar"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
os.makedirs(STATIC_ROOT, exist_ok=True)
MEDIA_ROOT = BASE_DIR / "media"          # pièces jointes, servies uniquement via une vue protégée
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

# Fichiers déposés : bucket privé Cloudflare R2 (API compatible S3) si configuré, sinon disque local
STORAGES = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
if os.environ.get("R2_BUCKET"):
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": {
        "bucket_name": os.environ["R2_BUCKET"],
        "endpoint_url": os.environ["R2_ENDPOINT"],
        "access_key": os.environ["R2_ACCESS_KEY_ID"],
        "secret_key": os.environ["R2_SECRET_ACCESS_KEY"],
        "region_name": "auto",
        "signature_version": "s3v4",
        "default_acl": None,          # bucket privé : aucun lien public
        "querystring_auth": True,
        "file_overwrite": False,      # deux fichiers de même nom ne s'écrasent pas
    }}
    if not re.fullmatch(r"https://[0-9a-f]{32}\.r2\.cloudflarestorage\.com/?", os.environ["R2_ENDPOINT"].strip()):
        logging.getLogger("config").error(
            "R2_ENDPOINT invalide : attendu https://<identifiant de compte Cloudflare, 32 caractères>"
            ".r2.cloudflarestorage.com (adresse « S3 API » du bucket, sans le nom du bucket). Les envois de fichiers échoueront.")

# Limites anti-abus (par processus) : tentatives de connexion et appels à l'IA
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
LOGIN_ECHECS_MAX = 5          # échecs autorisés par e-mail et par adresse IP...
LOGIN_BLOCAGE_SECONDES = 900  # ...avant un blocage de 15 minutes
IA_APPELS_PAR_HEURE = 20      # par utilisateur

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGGING = {"version": 1, "disable_existing_loggers": False,
           "handlers": {"console": {"class": "logging.StreamHandler"}},
           "root": {"handlers": ["console"], "level": "WARNING"},
           # 403/404 sont des refus normaux : seules les erreurs serveur (500) sont journalisées avec leur trace
           "loggers": {"django.request": {"level": "ERROR"}}}
