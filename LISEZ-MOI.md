# CIAT Incubateur - Plateforme de gestion de l'incubateur (Django)

Dépôt de dossier et de documents, évaluation par un comité, affectation de mentor et objectifs, jalons avec preuves,
commentaires et alertes de retard, calendrier, suivi à 3 et 6 mois, tableau de bord, comptes rendus rédigés avec l'IA,
exports PDF/Excel, assistant IA de rédaction. Backend Django 5, base SQLite, pages HTML (templates Django + CSS).

## Lancer (Python 3.10+)
- **Windows** : double-clic sur `lancer.bat`
- **Linux / Mac** : `./lancer.sh`
- À la main : `pip install -r requirements.txt`, puis
  `python manage.py makemigrations incubateur`, `python manage.py migrate`, `python manage.py seed`, `python manage.py runserver`

Ouvrir http://127.0.0.1:8000. `seed` crée 4 comptes de test et 30 projets fictifs (une seule fois).
Le dossier `incubateur/migrations/` est généré par `makemigrations` : gardez-le ensuite dans le dépôt.

## Comptes de test (mot de passe : `Passw0rd!`)
| Rôle | E-mail |
|---|---|
| Coordonnateur (accès aussi à /admin/) | coordo@ciat.sn |
| Comité | comite@ciat.sn |
| Mentor | mentor@ciat.sn (ou mentor2@ciat.sn) |
| Porteur de projet | porteur@ciat.sn |

## Assistant IA
Sans clé, mode démonstration. Pour une vraie IA : définir `ANTHROPIC_API_KEY` avant de lancer
(Windows : `set ANTHROPIC_API_KEY=votre_cle`). Ne jamais écrire la clé dans le code.
Le texte suggéré n'est enregistré qu'après relecture et validation du porteur.

## Tests
`python manage.py test` : CSRF, droits par rôle, dépôt, complétude, fichier interdit, évaluation, mentor, jalons,
objectifs, documents et preuves, commentaires, calendrier, suivis 3/6 mois, compte rendu IA, tableau de bord, exports,
assistant IA.

## Analyse des données
`python manage.py analyse` : indicateurs (sélection par cohorte, domaine et genre, grille d'évaluation, jalons,
suivis 3/6 mois, emplois) et contrôle de qualité des données. Résultats commentés dans `docs/rapport.md`.

## Déploiement (lien pour le jury)
Variables : `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` (valeur secrète longue), `DJANGO_ALLOWED_HOSTS` (ex. monsite.onrender.com),
`DJANGO_CSRF_ORIGINS` (ex. https://monsite.onrender.com). Commande de build : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py makemigrations incubateur && python manage.py migrate && python manage.py seed`.
Commande de démarrage : `gunicorn config.wsgi`. Attention : le stockage des hébergeurs gratuits est souvent temporaire (base et pièces jointes).

## Structure
- `config/` : réglages, routes principales
- `incubateur/` : models, views, forms, ia, admin, tests, commande `seed`
- `templates/`, `static/` : pages et style (couleurs de l'ISEP, logo)
- `media/` : pièces jointes (téléchargées uniquement via une vue protégée par rôle)

## Limites connues
Pas d'envoi d'e-mails (retards et suivis dus s'affichent dans l'application), pas de réinitialisation de mot de passe.
