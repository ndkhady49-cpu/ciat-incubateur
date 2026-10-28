# Rapport du projet — Plateforme de gestion de l'incubateur du CIAT

**Projet 2 — Évaluation pratique du cours d'Intelligence Artificielle Générative**
**ISEP Amadou Trawaré de Diamniadio**

---

## 1. Introduction

Ce rapport présente la conception, le développement, l'analyse des données et le déploiement d'une plateforme web de gestion de l'incubateur du CIAT (Centre d'Innovation, d'Application et de Transfert). L'application couvre le parcours complet d'un projet, de la soumission de l'idée au suivi à trois et six mois après l'incubation. Elle intègre l'IA générative à deux endroits : l'aide à la rédaction du dossier par le porteur et la préparation des comptes rendus de suivi par le mentor, toujours avec une validation humaine.

## 2. Équipe et répartition des rôles

Le travail a été réalisé par une équipe de quatre apprenants. Le profil développeur, qui concentre la plus grande part du travail (application, base de données, sécurité, IA, déploiement), a été porté par deux membres ; chacun a aussi contribué aux autres volets.

| Membre | Profil principal | Contributions |
|---|---|---|
| Ibrahima Thiam | Développeur | Développement de la plateforme Django : architecture, modèle de données, authentification et rôles, sécurité, intégration de l'IA, tests automatisés, déploiement (Render, Neon, Cloudflare R2) |
| Khady Ndiaye | Développeuse | Développement de la plateforme Django : architecture, modèle de données, authentification et rôles, sécurité, intégration de l'IA, tests automatisés, déploiement (Render, Neon, Cloudflare R2) |
| Issa Diome | Data analyst | Dictionnaire des données, jeu de données de démonstration, définition des indicateurs, tableau de bord et graphiques, contrôle de qualité (`manage.py analyse`), interprétation et recommandations |
| Ndeye Gnilane Sarr | Infographe | Identité visuelle conforme à la charte ISEP (palette brun et beige, typographie Inter), logo, maquettes, page d'accueil, ergonomie sur ordinateur et téléphone, supports de communication |

Responsabilités partagées : rédaction du cahier des charges, scénarios utilisateurs, guide utilisateur, journal des prompts et préparation de la démonstration.

## 3. Analyse du besoin

### 3.1 Problème identifié
Le CIAT gère plusieurs cohortes de porteurs de projets par an. Le processus implique la réception de dossiers, leur évaluation par un comité, l'affectation de mentors, le suivi par jalons, puis le suivi des projets après leur sortie de l'incubateur. Sans outil intégré, le coordonnateur doit jongler entre des tableurs, des e-mails et des documents papier, ce qui entraîne :

- des pertes d'information lors du passage d'une étape à l'autre ;
- des retards non détectés dans le suivi des jalons ;
- l'absence de suivi après l'incubation, donc aucune mesure de l'impact (emplois, chiffre d'affaires) ;
- l'impossibilité de produire rapidement des indicateurs de pilotage.

### 3.2 Solution proposée
Une application web centralisée permettant à chaque acteur (porteur, comité, mentor, coordonnateur) d'intervenir dans son périmètre, avec un tableau de bord filtrable, des alertes, un calendrier des échéances et des exports automatisés.

### 3.3 Scénarios utilisateurs exploités
1. **Scénario porteur** : un étudiant soumet un projet « Irrigation connectée », reçoit un retour « À compléter », utilise l'assistant IA pour reformuler son problème, ajoute un budget prévisionnel au dossier, puis resoumet. Une fois accepté, il dépose les preuves de ses jalons et échange avec son mentor.
2. **Scénario mentor** : la mentore fixe les objectifs d'accompagnement, valide les jalons au vu des preuves, commente, puis génère avec l'IA un brouillon de compte rendu qu'elle corrige avant de l'enregistrer en PDF.
3. **Scénario coordonnateur** : le responsable du CIAT filtre les projets par cohorte, repère les jalons en retard et les suivis à 3 ou 6 mois non réalisés, consulte le calendrier du mois, puis exporte un fichier Excel pour un rapport au directeur.

## 4. Choix techniques

### 4.1 Architecture
L'application suit le modèle MVT de Django (Model-View-Template). Le backend Python gère la logique métier et les droits, PostgreSQL stocke les données, et les templates HTML produisent l'interface.

| Composant | Technologie | Justification |
|---|---|---|
| Framework | Django 5 | Maturité, sécurité intégrée (CSRF, auth), ORM |
| Base de données | PostgreSQL (Neon) en production, SQLite en local | Données persistantes et sauvegardées ; aucune installation en développement |
| Fichiers déposés | Cloudflare R2 (bucket privé) | Fichiers conservés entre les déploiements, jamais accessibles par lien public |
| IA | API Groq (`openai/gpt-oss-120b`), Claude en option | Offre gratuite suffisante pour le volume du CIAT ; fournisseur interchangeable par une variable ; mode démonstration sans clé |
| Graphiques | Chart.js | Graphiques interactifs (survol, légendes cliquables) |
| Export PDF | ReportLab | Génération de fiches et comptes rendus |
| Export Excel | openpyxl | Format .xlsx natif, plusieurs feuilles |
| Hébergement | Render (gratuit) | Déploiement automatique depuis GitHub |
| Fichiers statiques | WhiteNoise | Pas besoin de serveur Nginx |

### 4.2 Modèle de données
Huit entités (détail dans `docs/schema_base_de_donnees.md`) :

- **User** : 4 rôles, e-mail comme identifiant, genre facultatif pour les statistiques.
- **Projet** : dossier, statut, mentor, objectifs et date de fin d'incubation.
- **Evaluation** : grille sur 4 critères notés de 0 à 5, décision et motivation obligatoire.
- **Jalon** : échéance, statut et retard calculé.
- **Document** : pièce du dossier ou preuve rattachée à un jalon.
- **Commentaire** : échange sur le projet ou sur un jalon.
- **Suivi** : bilan à 3 ou 6 mois (situation, emplois, chiffre d'affaires), un seul par période.
- **CompteRendu** : texte validé, avec la mention d'une éventuelle aide de l'IA.

### 4.3 Rôles et droits

| Action | Porteur | Comité | Mentor | Coordonnateur |
|---|---|---|---|---|
| Déposer et modifier son dossier | ✅ (le sien) | | | |
| Ajouter des documents et des preuves | ✅ (le sien) | | ✅ (ses projets) | ✅ |
| Évaluer et décider | | ✅ | | ✅ |
| Affecter un mentor | | | | ✅ |
| Fixer objectifs, jalons, suivis | | | ✅ (ses projets) | ✅ |
| Commenter | ✅ | ✅ | ✅ | ✅ |
| Compte rendu de suivi | lecture PDF | lecture PDF | ✅ | ✅ |
| Tableau de bord | | ✅ | | ✅ |
| Export Excel, administration | | | | ✅ |

### 4.4 Sécurité
- Protection CSRF sur tous les formulaires POST.
- Contrôle d'accès dans chaque vue : rôle et appartenance au projet, sinon erreur 403.
- Une preuve ou un commentaire ne peut viser qu'un jalon du même projet (vérifié côté serveur).
- Fichiers : extensions autorisées (pdf, png, jpg, docx, xlsx) et 5 Mo maximum. Ils sont servis par une vue protégée, jamais par un lien direct vers `media/`.
- Mots de passe : 8 caractères minimum, rejet des mots de passe courants.
- Connexion bloquée 15 minutes après 5 échecs (par e-mail ou par adresse IP) ; 20 appels à l'IA par utilisateur et par heure.
- Chaque utilisateur peut changer son mot de passe ; le coordonnateur réinitialise un mot de passe oublié dans l'administration.
- En production : `DEBUG` désactivé, clé secrète obligatoire (le site refuse de démarrer sans), cookies sécurisés, HSTS.
- Aucun mot de passe dans le code : le compte coordonnateur réel et les comptes de démonstration sont créés à partir
  de variables secrètes ; les comptes de démonstration n'ont pas accès à l'administration.

## 5. Intégration de l'IA générative

### 5.1 Fonctionnalités
1. **Assistant de rédaction (porteur)** : reformulation, pitch de 4 phrases ou analyse SWOT, à partir du texte du porteur, pour les champs « Problème » et « Solution ».
2. **Compte rendu de suivi (mentor, coordonnateur)** : l'application construit un résumé factuel du projet (objectifs, jalons et leur état, preuves, derniers commentaires, suivis), puis demande à l'IA un compte rendu en quatre parties : situation, avancement, points de vigilance, prochaines étapes.

### 5.2 Garde-fous
- **Validation humaine obligatoire** : aucun texte de l'IA n'est enregistré sans relecture et clic explicite.
- **Données fournies uniquement** : pour le compte rendu, l'IA ne reçoit que le résumé factuel et doit écrire « non renseigné » quand une information manque.
- **Traçabilité** : `ia_used` est enregistré sur le projet et sur le compte rendu, et la mention « rédigé avec l'aide d'une IA » apparaît à l'écran et dans le PDF.
- **Mode démonstration** : sans clé API, l'assistant renvoie un modèle de texte et le compte rendu est construit à partir des données du projet. La démonstration fonctionne donc sans dépendre d'un service externe.
- **Données personnelles** : l'interface invite à ne pas saisir de données sensibles ; seuls le nom du porteur et du mentor figurent dans le résumé envoyé.

### 5.3 Implémentation
Le fournisseur est choisi par une variable d'environnement. Par défaut, l'application utilise **Groq**, dont l'offre gratuite suffit au volume du CIAT : SDK officiel `groq`, modèle ouvert `openai/gpt-oss-120b` (un modèle qui raisonne avant de répondre ; seule la réponse finale est conservée, `include_reasoning=False`), effort de raisonnement moyen. L'API Claude d'Anthropic (SDK `anthropic`, modèle `claude-opus-5`) reste disponible en option. Délai maximal de 25 secondes et une seule nouvelle tentative. En cas de clé invalide, de limite gratuite atteinte (30 requêtes par minute, 1 000 par jour), de réponse tronquée ou d'erreur réseau, l'application bascule sur le mode démonstration et l'incident est journalisé, sans jamais écrire la clé.

## 6. Données et indicateurs

### 6.1 Jeu de données
La commande `python manage.py seed` crée un jeu de données **fictif et reproductible** (générateur aléatoire initialisé) : 4 comptes de test, 12 porteurs supplémentaires, 30 projets répartis sur 2 cohortes et 7 domaines prioritaires du CIAT, avec leurs évaluations, jalons, objectifs, commentaires et suivis à 3 et 6 mois. Les dates sont calculées par rapport au jour de création, donc les retards évoluent avec le temps. Aucune donnée réelle de porteur n'est utilisée.

### 6.2 Définition des indicateurs

| Indicateur | Définition et calcul | Usage |
|---|---|---|
| Dossiers déposés | Nombre de projets correspondant aux filtres | Volume d'activité |
| Taux de sélection | Acceptés ÷ (acceptés + refusés). Les dossiers « soumis » et « à compléter » sont exclus car non décidés | Sélectivité du comité |
| Complétude | Part des 5 éléments renseignés : titre, domaine, problème, solution, au moins une pièce jointe | Qualité des dossiers |
| Jalons validés / en cours / à faire / en retard | Catégories exclusives : un jalon non validé dont l'échéance est passée compte uniquement « en retard » | Avancement global |
| Avancement des jalons | Jalons validés ÷ total des jalons | Progression des projets |
| Suivis dus | Suivis à 3 ou 6 mois dont l'échéance (fin d'incubation + 90 ou + 180 jours) est passée et qui ne sont pas saisis | Rigueur du suivi |
| Emplois créés | Somme des emplois déclarés dans les suivis | Impact de l'incubateur |
| Mentors actifs | Mentors ayant au moins un projet dans la sélection | Charge d'accompagnement |
| Projets avec IA | Projets dont un texte validé a été rédigé avec l'IA | Adoption de l'assistant |

Le tableau de bord les présente avec des filtres par cohorte, domaine et statut. Les mêmes indicateurs, ventilés par cohorte, domaine et genre, sont recalculables avec `python manage.py analyse`.

### 6.3 Contrôle de qualité
La qualité est assurée à deux niveaux :

- **À la saisie** : champs obligatoires, listes de choix fermées (domaines, statuts, situations), notes bornées de 0 à 5, dates validées, un seul suivi par période, extension et taille des fichiers vérifiées.
- **Après coup** : `python manage.py analyse` vérifie la cohérence des données. Résultat sur le jeu de démonstration du 27/10/2026 :

| Contrôle | Résultat | Commentaire |
|---|---|---|
| Projets acceptés sans mentor, sans objectifs ou sans jalon | 0 | Cohérent |
| Projets décidés sans évaluation | 0 | Chaque décision est motivée |
| Statut différent de la dernière décision du comité | 0 | Cohérent |
| Mentor affecté à un projet non accepté | 0 | Règle respectée |
| Porteurs sans genre renseigné | 0 | Le champ reste facultatif en production |
| Dossiers incomplets | 30 | Le jeu fictif ne contient pas de fichiers |
| Jalons validés sans preuve | 31 | Voir l'interprétation ci-dessous |

## 7. Analyse et interprétation

Les chiffres ci-dessous proviennent du jeu de **démonstration** (30 projets fictifs, état au 27/10/2026). Ils illustrent la démarche d'analyse et la lecture du tableau de bord ; ils ne décrivent pas l'activité réelle du CIAT.

### 7.1 Sélection
- 30 dossiers : 17 acceptés, 5 refusés, 4 à compléter, 4 en attente. **Taux de sélection : 77 %**, identique entre les cohortes 2026-A (77 %) et 2026-B (78 %).
- Les domaines « Éducation, formation et insertion » (9 dossiers) et « Services aux collectivités » (7) concentrent la moitié des candidatures. « Énergie » (2 dossiers, aucun accepté) et « Agriculture » (2) sont peu représentés, alors que ce sont des domaines prioritaires du CIAT.
- Le taux de sélection est de 91 % pour les porteuses et de 64 % pour les porteurs. Sur 14 et 16 dossiers, l'écart ne permet aucune conclusion, mais l'indicateur doit être suivi quand le volume augmente.

**Lecture critique de la grille d'évaluation.** La note moyenne des projets acceptés (13,6/20) est égale à celle des projets refusés (13,6/20), et les « à compléter » obtiennent 14,5/20. Dans les données fictives, les notes sont aléatoires, donc ce résultat est attendu. Mais en conditions réelles, le même constat signifierait que la décision ne suit pas la grille. Le tableau de bord permet de le détecter.

### 7.2 Accompagnement
- 68 jalons : 31 validés (46 %), 4 en retard (6 %), 33 à venir. 3 projets accompagnés sur 17 ont au moins un retard. Le niveau de retard est faible, et les alertes permettent d'agir projet par projet.
- **Aucun des 31 jalons validés n'a de preuve associée.** La validation repose donc sur la seule déclaration du mentor, ce qui fragilise la traçabilité demandée par le CIAT.

### 7.3 Suivi après l'incubation
- 13 suivis réalisés sur 17 attendus (76 %) : 4 suivis sont en retard et apparaissent dans les alertes du tableau de bord.
- Situation déclarée : 7 projets en pause, 4 arrêtés, 1 actif et 1 en croissance. **11 suivis sur 13 montrent un projet en pause ou arrêté.**
- 46 emplois déclarés au total sur l'ensemble des suivis.

## 8. Recommandations

1. **Exiger une preuve avant de valider un jalon.** Ce serait une règle simple à ajouter dans l'application, et elle rendrait l'avancement vérifiable.
2. **Calibrer la grille d'évaluation.** Fixer un seuil indicatif (par exemple 12/20 minimum pour une acceptation) et demander une motivation renforcée quand la décision s'en écarte. Comparer chaque trimestre les notes moyennes par décision.
3. **Renforcer l'accompagnement après la sortie.** Avec une majorité de projets en pause ou arrêtés à 3 et 6 mois, il faut prévoir un point mentor à mi-parcours du suivi et orienter vers des partenaires financiers dès la fin d'incubation.
4. **Lancer des appels ciblés** sur les domaines prioritaires peu représentés (énergie, agriculture, mécanique), par exemple avec les départements de l'ISEP concernés.
5. **Réaliser les suivis à l'échéance.** Le coordonnateur peut traiter chaque semaine la liste « Suivis à réaliser » du tableau de bord ; l'objectif est 100 % de suivis réalisés.
6. **Suivre l'équité.** Garder les indicateurs par genre et par cohorte dans le rapport annuel, et les interpréter quand le volume dépasse quelques dizaines de dossiers.

## 9. Protection des données

- Le genre est facultatif et sert uniquement aux statistiques agrégées.
- Les pièces jointes ne sont accessibles qu'aux personnes autorisées sur le projet.
- Le porteur ne voit que ses projets, le mentor que les projets qui lui sont affectés.
- Les données envoyées à l'IA se limitent au texte saisi par le porteur ou au résumé factuel du projet ; l'interface rappelle de ne pas y mettre de données sensibles.
- Les exports Excel sont réservés au coordonnateur.

## 10. Résultats

### 10.1 Fonctionnalités livrées
- ✅ Inscription, connexion, profil modifiable
- ✅ Dépôt de dossier, contrôle de complétude, documents multiples
- ✅ Grille d'évaluation sur 4 critères (/20), décision motivée
- ✅ Affectation de mentor et objectifs d'accompagnement
- ✅ Jalons avec preuves, commentaires et alertes de retard
- ✅ Calendrier mensuel des échéances
- ✅ Suivi à 3 et 6 mois avec alertes
- ✅ Tableau de bord filtrable, graphiques interactifs
- ✅ Comptes rendus de suivi rédigés avec l'IA, export PDF
- ✅ Exports PDF (fiche projet, compte rendu) et Excel (projets, jalons, suivis)
- ✅ Assistant IA de rédaction avec validation humaine

### 10.2 Tests automatisés
27 tests couvrent les parcours critiques (`python manage.py test`, 27/27 OK, sur SQLite et PostgreSQL) :

1. Accès protégé et vérification CSRF.
2. Dépôt de dossier et calcul de complétude.
3. Rejet d'un fichier interdit (.exe).
4. Parcours complet : évaluation, affectation, jalons, tableau de bord, exports.
5. Suggestion IA en mode démonstration, puis validation.
6. Objectifs, fin d'incubation et suivis à 3/6 mois (doublon refusé, porteur interdit).
7. Documents et preuves : droits d'accès, jalon d'un autre projet refusé.
8. Commentaires et calendrier filtré selon le rôle.
9. Compte rendu : brouillon IA non enregistré, validation, PDF.
10. Tableau de bord : catégories de jalons exclusives et proportions exactes.
11. Connexion bloquée après 5 échecs, puis rétablie.
12. Changement de mot de passe.
13. Refus après réévaluation : le mentor est retiré.
14. Cohorte par défaut et modification réservée au coordonnateur.
15. Quota d'appels à l'IA.
16. Création du compte coordonnateur, démonstration avec mot de passe secret et sans accès admin, suppression de la démonstration.
17. Pages d'erreur 403 et 404.
18. Réglages de production : PostgreSQL, stockage R2 privé, clé secrète obligatoire, alerte si l'adresse R2 est invalide.
19-21. Assistant Claude (API simulée) : réponse, refus des filtres de sécurité, clé invalide.
22-25. Assistant Groq (API simulée) : réponse, limite gratuite atteinte, réponse tronquée, choix du fournisseur.
26-27. Stockage de fichiers en panne : dossier enregistré sans pièce jointe, document refusé proprement, téléchargement sans erreur 500.

### 10.3 Anomalies relevées et corrigées
| Anomalie | Correction |
|---|---|
| Graphique des jalons : « À faire » toujours à 0 et jalons en retard comptés deux fois | Calcul des catégories exclusives côté serveur |
| Colonne « Proportion » affichant le nombre au lieu du pourcentage | Pourcentage calculé dans la vue |
| Styles du tableau de bord absents de la feuille CSS | Styles ajoutés |
| Fiche PDF tronquée quand le texte dépasse une page | Saut de page automatique |
| Compte coordonnateur de démonstration administrateur avec un mot de passe publié | Compte réel créé par variables secrètes ; démonstration sans accès admin, mot de passe secret |
| Base et fichiers effacés à chaque redéploiement | PostgreSQL Neon et Cloudflare R2 |
| Migrations générées en production | Migrations versionnées, seulement appliquées au déploiement |
| Tous les projets classés dans la cohorte « 2026-A » | Cohorte calculée selon le semestre de dépôt, modifiable par le coordonnateur |
| Projet refusé après réévaluation mais toujours suivi par un mentor | Le mentor est retiré si la décision n'est plus « accepté » |
| Aucune limite de tentatives de connexion ni d'appels à l'IA | Blocage temporaire et quota horaire |
| Impossible de changer son mot de passe | Page « Changer mon mot de passe » |
| Erreur 500 au dépôt d'un dossier avec pièce jointe, en production (adresse R2 restée à sa valeur d'exemple) | Adresse corrigée ; le dossier est désormais enregistré même si le stockage est indisponible, et une adresse invalide est signalée au démarrage |

## 11. Déploiement

- **URL** : https://ciat-incubateur.onrender.com
- **Architecture** : Render (application) + Neon (PostgreSQL, région Europe) + Cloudflare R2 (fichiers).
- **Build** (`build.sh`) : dépendances, fichiers statiques, migrations, création du compte coordonnateur réel,
  comptes de démonstration pour le jury (une seule fois, si `SEED_DEMO=1`). Détail dans `docs/deploiement.md`.
- **Démarrage** : `gunicorn config.wsgi`
- **Variables d'environnement** : `DATABASE_URL`, `R2_*`, `CIAT_ADMIN_*`, `DEMO_PASSWORD`, `DJANGO_DEBUG=0`,
  `DJANGO_SECRET_KEY`, `GROQ_API_KEY` (facultative ; `ANTHROPIC_API_KEY` en option), toutes saisies dans Render et jamais dans le code.

## 12. Limites et perspectives

### 12.1 Limites actuelles
- Pas d'envoi d'e-mails : les alertes ne sont visibles que dans l'application.
- Pas de réinitialisation de mot de passe en libre-service par e-mail (elle passe par le coordonnateur).
- Offre gratuite de Render : mise en veille après 15 minutes sans visite (premier chargement lent).
- Les limites anti-abus sont comptées par processus serveur (suffisant avec un seul processus, à revoir si le service grandit).
- Les analyses portent sur des données fictives ; elles devront être refaites sur les données réelles du CIAT.

### 12.2 Améliorations possibles
- Rendre la preuve obligatoire pour valider un jalon (recommandation 1).
- Envoyer les alertes de retard et de suivi par e-mail.
- Ajouter la réinitialisation du mot de passe par e-mail.

## 13. Conclusion

La plateforme CIAT Incubateur couvre l'ensemble du parcours demandé pour le projet 2 : dépôt, évaluation, accompagnement, suivi après incubation et production de comptes rendus. Le tableau de bord et la commande d'analyse transforment les données saisies en indicateurs de décision, et leur lecture a déjà fait apparaître des points d'amélioration concrets : preuves des jalons, calibrage de la grille, accompagnement après la sortie. L'IA générative accélère la rédaction des dossiers et des comptes rendus, sans jamais se substituer à la validation humaine.
