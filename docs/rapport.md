# Rapport du projet — Plateforme de gestion de l'incubateur du CIAT

**Projet 2 — Évaluation pratique du cours d'Intelligence Artificielle Générative**
**ISEP Amadou Trawaré de Diamniadio**

---

## 1. Introduction

Ce rapport présente la conception, le développement et le déploiement d'une plateforme web de gestion de l'incubateur du CIAT (Centre d'Innovation, d'Application et de Transfert). L'application répond au besoin de dématérialiser le processus de soumission, d'évaluation et de suivi des projets incubés, tout en intégrant un assistant d'intelligence artificielle générative pour aider les porteurs de projets à rédiger leur dossier.

## 2. Analyse du besoin

### 2.1 Problème identifié
Le CIAT gère plusieurs cohortes de porteurs de projets par an. Le processus implique la réception de dossiers, leur évaluation par un comité, l'affectation de mentors et le suivi par jalons. Sans outil intégré, le coordonnateur doit jongler entre des tableurs, des e-mails et des documents papier, ce qui entraîne :
- Des pertes d'information lors du passage d'une étape à l'autre.
- Des retards non détectés dans le suivi des jalons.
- L'impossibilité de produire rapidement des indicateurs de pilotage.

### 2.2 Solution proposée
Une application web centralisée permettant à chaque acteur (porteur, comité, mentor, coordonnateur) d'intervenir dans son périmètre, avec un tableau de bord temps réel et des exports automatisés.

### 2.3 Utilisateurs interrogés
Deux scénarios utilisateurs ont été exploités :
1. **Scénario porteur** : un étudiant soumet un projet « Irrigation connectée », reçoit un retour « À compléter », utilise l'assistant IA pour reformuler son problème, puis resoumet.
2. **Scénario coordonnateur** : le responsable du CIAT filtre les projets par cohorte, identifie les jalons en retard, exporte un fichier Excel pour un rapport au directeur.

## 3. Choix techniques

### 3.1 Architecture
L'application suit le modèle **MVC** de Django (Model-View-Template). Le backend Python gère la logique métier, la base SQLite stocke les données, et les templates HTML produisent l'interface.

| Composant | Technologie | Justification |
|---|---|---|
| Framework | Django 5 | Maturité, sécurité intégrée (CSRF, auth), ORM puissant |
| Base de données | SQLite | Suffisant pour le volume (< 100 projets), zéro configuration |
| IA | API Anthropic (Claude) | Qualité du français, mode fallback sans clé |
| Export PDF | ReportLab | Génération programmatique de PDF |
| Export Excel | openpyxl | Format .xlsx natif |
| Hébergement | Render (gratuit) | Déploiement simple depuis GitHub |
| Serveur statique | WhiteNoise | Fichiers statiques sans serveur Nginx |

### 3.2 Modèle de données
Quatre entités principales :
- **User** (extends AbstractUser) : 4 rôles, e-mail comme identifiant.
- **Projet** : dossier soumis par un porteur, avec statut et mentor.
- **Evaluation** : notation sur 4 critères + décision + motivation.
- **Jalon** : point de suivi avec échéance et alerte de retard.

### 3.3 Sécurité
- Protection CSRF sur tous les formulaires POST.
- Contrôle d'accès par rôle : chaque vue vérifie le rôle de l'utilisateur, retour 403 si non autorisé.
- Validation des fichiers : extension (pdf, png, jpg, docx) et taille (5 Mo max).
- Pièces jointes servies via une vue protégée (pas d'accès direct au dossier `media/`).
- Mot de passe : 8 caractères minimum, rejet des mots de passe courants et numériques.

## 4. Intégration de l'IA générative

### 4.1 Fonctionnalité
L'assistant IA aide les porteurs à rédiger les champs « Problème » et « Solution » de leur dossier. Trois modes sont proposés :
- **Reformuler** : réécrire un brouillon de façon claire et professionnelle.
- **Pitch** : générer un pitch de 4 phrases.
- **SWOT** : produire une analyse Forces/Faiblesses/Opportunités/Menaces.

### 4.2 Garde-fous
- **Validation humaine obligatoire** : le texte suggéré n'est enregistré dans le dossier qu'après relecture et clic explicite du porteur.
- **Traçabilité** : le champ `ia_used` du projet passe à True, et l'interface affiche la mention « rédigé avec l'aide d'une IA ».
- **Refus d'invention** : le prompt système interdit à l'IA d'inventer des faits absents du texte fourni.
- **Mode démonstration** : sans clé API, l'application fonctionne avec des modèles textuels statiques.

### 4.3 Implémentation
L'appel à l'API Anthropic se fait via `requests.post()` avec un timeout de 30 secondes. Le modèle utilisé est `claude-sonnet-4-6` (configurable via la variable d'environnement `ANTHROPIC_MODEL`).

## 5. Résultats

### 5.1 Fonctionnalités livrées
Les 7 fonctionnalités du cahier des charges sont implémentées :
- ✅ Inscription, connexion, profil modifiable
- ✅ Dépôt de dossier avec contrôle de complétude
- ✅ Évaluation par le comité (grille 4 critères /20)
- ✅ Affectation de mentor
- ✅ Suivi des jalons avec alertes de retard
- ✅ Tableau de bord filtrable avec indicateurs
- ✅ Exports PDF et Excel
- ✅ Assistant IA avec validation humaine

### 5.2 Tests automatisés
5 tests unitaires couvrent les parcours critiques :
1. Accès protégé et vérification CSRF.
2. Dépôt de dossier et calcul de complétude.
3. Rejet de fichier interdit (.exe).
4. Parcours complet : évaluation → affectation → jalons → dashboard → exports.
5. Suggestion IA en mode démonstration + validation.

Tous les tests passent (`python manage.py test` → 5/5 OK).

### 5.3 Données de démonstration
La commande `python manage.py seed` crée :
- 4 comptes de test (coordonnateur, comité, mentor ×2, porteur).
- 12 porteurs supplémentaires avec des noms sénégalais.
- 30 projets fictifs répartis sur 2 cohortes et 7 domaines.
- Des évaluations et jalons associés.

## 6. Déploiement

L'application est déployée sur Render.com :
- **URL** : https://ciat-incubateur.onrender.com
- **Build** : installation des dépendances, collectstatic, migrations, seed.
- **Start** : `gunicorn config.wsgi`
- **Variables d'environnement** : `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY` (générée), `PYTHON_VERSION=3.12.3`.

## 7. Limites et perspectives

### 7.1 Limites actuelles
- Pas d'envoi d'e-mails (les notifications sont uniquement dans l'application).
- Pas de réinitialisation de mot de passe en self-service.
- Base SQLite éphémère sur Render gratuit (les données sont réinitialisées à chaque redéploiement).
- Pas de fichiers joints sur les jalons individuels.

### 7.2 Améliorations possibles
- Migrer vers PostgreSQL pour une base persistante.
- Ajouter l'envoi d'e-mails pour les alertes de retard.
- Intégrer une vue calendrier pour visualiser les jalons.
- Permettre l'upload de preuves sur chaque jalon.
- Ajouter la réinitialisation de mot de passe par e-mail.

## 8. Conclusion

La plateforme CIAT Incubateur répond aux besoins exprimés dans le cahier des charges. Elle offre une gestion complète du cycle de vie d'un projet incubé, de la soumission au suivi post-acceptation. L'intégration de l'IA générative, encadrée par une validation humaine obligatoire, accélère la rédaction des dossiers tout en garantissant la transparence. Le déploiement sur Render permet au jury d'accéder à une démonstration fonctionnelle avec des données réalistes.
