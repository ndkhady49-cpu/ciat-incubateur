# Cahier des charges — Plateforme de gestion de l'incubateur du CIAT

## 1. Contexte

Le Centre d'Innovation, d'Application et de Transfert (CIAT) de l'ISEP Amadou Trawaré de Diamniadio accompagne les porteurs de projets à travers un incubateur. La gestion actuelle repose sur des outils non intégrés (tableurs, e-mails, documents papier), ce qui entraîne des pertes d'information, des retards dans le suivi et une difficulté à produire des indicateurs fiables.

Le présent projet vise à développer une **application web** permettant de gérer le parcours complet d'un projet incubé, de la soumission à l'évaluation, en passant par l'affectation d'un mentor et le suivi des jalons.

## 2. Utilisateurs cibles

| Profil | Description | Effectif estimé |
|---|---|---|
| **Porteur de projet** | Étudiant ou porteur externe soumettant un dossier d'incubation | 20-50 par cohorte |
| **Membre du comité** | Évaluateur examinant et notant les dossiers soumis | 3-5 |
| **Mentor** | Accompagnateur assigné aux projets acceptés | 5-10 |
| **Coordonnateur** | Responsable du CIAT, pilote l'ensemble du processus | 1-2 |

## 3. Exigences fonctionnelles

### 3.1 Gestion des comptes et profils (Priorité haute)
- Inscription par e-mail avec mot de passe sécurisé (8 caractères minimum).
- Connexion par e-mail (identifiant unique).
- Modification du profil (nom, genre).
- Quatre rôles avec droits différenciés.

### 3.2 Dépôt et gestion de dossier (Priorité haute)
- Formulaire de dépôt : titre, domaine, problème identifié, solution proposée.
- Pièce jointe (PDF, PNG, JPG, DOCX — 5 Mo max).
- Contrôle de complétude avec indicateur visuel (jauge %).
- Modification possible tant que le dossier est en statut « Soumis » ou « À compléter ».

### 3.3 Évaluation par le comité (Priorité haute)
- Grille de notation sur 4 critères : Innovation, Faisabilité, Impact, Équipe (chacun de 0 à 5, total /20).
- Décision motivée : Accepté, Refusé, ou À compléter.
- Le statut du projet est mis à jour automatiquement.

### 3.4 Affectation de mentor (Priorité haute)
- Le coordonnateur affecte un mentor uniquement aux projets acceptés.
- Le mentor accède aux projets qui lui sont affectés.

### 3.5 Suivi des jalons (Priorité haute)
- Création de jalons par le coordonnateur ou le mentor (titre + échéance).
- Trois statuts : À faire, En cours, Validé.
- Commentaire associé à chaque jalon.
- Alertes visuelles pour les jalons en retard (échéance dépassée).

### 3.6 Tableau de bord décisionnel (Priorité haute)
- Filtrage par cohorte, domaine et statut.
- Indicateurs : nombre de dossiers, taux de sélection, jalons en retard, avancement.
- Répartition par domaine, par cohorte, par genre.
- Barres de progression visuelles.

### 3.7 Exports (Priorité moyenne)
- Export Excel de tous les projets (titre, porteur, domaine, statut, mentor, complétude).
- Fiche PDF individuelle par projet.

### 3.8 Assistant IA de rédaction (Priorité moyenne)
- Trois modes : Reformuler, Pitch, Analyse SWOT.
- Suggestion générée par l'API Anthropic (ou mode démonstration sans clé).
- Le texte n'est enregistré qu'après validation explicite par le porteur.
- Marqueur « rédigé avec l'aide d'une IA » sur le dossier.

### 3.9 Administration (Priorité basse)
- Interface Django Admin pour le coordonnateur.
- Gestion des utilisateurs, projets, évaluations et jalons.

## 4. Exigences non fonctionnelles

| Critère | Exigence |
|---|---|
| **Sécurité** | Protection CSRF sur tous les formulaires, contrôle d'accès par rôle (403), validation des fichiers (extension + taille) |
| **Performance** | Temps de réponse < 2 secondes sur un hébergement standard |
| **Responsive** | Interface utilisable sur mobile (320px) et ordinateur |
| **Accessibilité** | Taille de clic minimum 44px, labels sur tous les champs |
| **Déploiement** | Compatible Render (plan gratuit), WhiteNoise pour les fichiers statiques |
| **Données** | Commande `seed` pour générer 30 projets fictifs de démonstration |

## 5. Contraintes techniques

| Élément | Choix |
|---|---|
| Langage | Python 3.12 |
| Framework | Django 5.x |
| Base de données | SQLite (suffisant pour le volume attendu) |
| IA | API Anthropic (Claude) avec fallback mode démo |
| Export PDF | ReportLab |
| Export Excel | openpyxl |
| Serveur statique | WhiteNoise |
| Serveur WSGI | Gunicorn |
| Hébergement | Render.com (plan gratuit) |

## 6. Priorités de développement

1. **MVP** : Inscription, dépôt, évaluation, changement de statut.
2. **V1** : Mentor, jalons, alertes, tableau de bord, exports.
3. **V2** : Assistant IA, page profil, améliorations design.

## 7. Limites connues et acceptées

- Pas d'envoi d'e-mails (notifications uniquement dans l'application).
- Pas de réinitialisation de mot de passe en self-service.
- Le suivi à 3 et 6 mois est géré via les jalons (pas de module dédié).
- Pas de pièces jointes sur les jalons individuels.
- Base SQLite éphémère sur Render (réinitialisée à chaque redéploiement gratuit).
