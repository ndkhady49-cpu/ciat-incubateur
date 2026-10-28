# CIAT Incubateur - Plateforme de gestion de l'incubateur (Django)

Dépôt de dossier et de documents, évaluation par un comité, affectation de mentor et objectifs, jalons avec preuves,
commentaires et alertes de retard, calendrier, suivi à 3 et 6 mois, tableau de bord, comptes rendus rédigés avec l'IA,
exports PDF/Excel, assistant IA de rédaction. Backend Django 5, base SQLite, pages HTML (templates Django + CSS).

## Lancer (Python 3.10+)
- **Windows** : double-clic sur `lancer.bat`
- **Linux / Mac** : `./lancer.sh`
- À la main : `pip install -r requirements.txt`, puis
  `python manage.py migrate`, `python manage.py seed`, `python manage.py runserver`

Ouvrir http://127.0.0.1:8000. En local, la base est SQLite (`db.sqlite3`) et les fichiers vont dans `media/`.
`seed` crée les comptes de démonstration et 30 projets fictifs (une seule fois).
Après une modification de `models.py` : `python manage.py makemigrations incubateur` en local, puis versionner
la migration créée (la production applique seulement `migrate`).

## Comptes de démonstration
En local, mot de passe `Passw0rd!`. En production, mot de passe défini par la variable secrète `DEMO_PASSWORD`
et communiqué au jury uniquement. Ces comptes n'ont pas accès à `/admin/`.
| Rôle | E-mail |
|---|---|
| Coordonnateur | coordo@ciat.sn |
| Comité | comite@ciat.sn |
| Mentor | mentor@ciat.sn (ou mentor2@ciat.sn) |
| Porteur de projet | porteur@ciat.sn |

## Assistant IA
Fournisseur par défaut : **Groq** (offre gratuite, modèle `openai/gpt-oss-120b`), clé `GROQ_API_KEY`. Claude reste
possible avec `ANTHROPIC_API_KEY` et `IA_FOURNISSEUR=anthropic`. Détails : `docs/deploiement.md` § 6.
Sans clé, mode démonstration. Pour une vraie IA : définir `GROQ_API_KEY` avant de lancer
(Windows : `set GROQ_API_KEY=votre_cle`). Ne jamais écrire la clé dans le code.
Le texte suggéré n'est enregistré qu'après relecture et validation du porteur.

## Tests
`python manage.py test` : CSRF, droits par rôle, dépôt, complétude, fichier interdit, évaluation, mentor, jalons,
objectifs, documents et preuves, commentaires, calendrier, suivis 3/6 mois, compte rendu IA, tableau de bord, exports,
assistant IA.

## Analyse des données
`python manage.py analyse` : indicateurs (sélection par cohorte, domaine et genre, grille d'évaluation, jalons,
suivis 3/6 mois, emplois) et contrôle de qualité des données. Résultats commentés dans `docs/rapport.md`.

## Déploiement (https://ciat-incubateur.onrender.com)
Render (serveur) + Neon (PostgreSQL) + Cloudflare R2 (fichiers) : les données sont conservées entre les déploiements.
Procédure complète, variables d'environnement et exploitation : **`docs/deploiement.md`**.
Build : `bash build.sh` (migrations, compte coordonnateur réel via `init_coordo`, démonstration si `SEED_DEMO=1`).
Démarrage : `gunicorn config.wsgi`.

## Structure
- `config/` : réglages, routes principales
- `incubateur/` : models, views, forms, ia, admin, tests, commande `seed`
- `templates/`, `static/` : pages et style (couleurs de l'ISEP, logo)
- `media/` : pièces jointes (téléchargées uniquement via une vue protégée par rôle)

## Limites connues
Pas d'envoi d'e-mails (retards et suivis dus s'affichent dans l'application) ; un mot de passe oublié est
réinitialisé par le coordonnateur dans `/admin/` (chaque utilisateur peut changer le sien dans « Mon profil »).
