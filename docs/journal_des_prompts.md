# Journal des prompts — Utilisation de l'IA générative dans le projet

Ce document recense les prompts significatifs utilisés lors du développement et dans l'application elle-même, les résultats obtenus, et les corrections apportées.

---

## 1. Prompts intégrés dans l'application

L'assistant IA de l'application utilise trois prompts prédéfinis, envoyés à l'API Anthropic (Claude) :

### Prompt système (commun à tous les modes)
```
Tu aides des porteurs de projet d'un incubateur sénégalais. Réponds en français,
sans inventer de faits absents du texte.
```
**Justification** : le garde-fou « sans inventer de faits absents du texte » empêche l'IA de fabriquer des informations. Le contexte sénégalais oriente le ton et le vocabulaire.

### Prompt « Reformuler »
```
Reformule ce texte de façon claire et professionnelle.

[texte du porteur]
```
**Résultat typique** : le brouillon « on manque d'eau pour les champs » devient « Les exploitations agricoles de la zone souffrent d'un déficit hydrique chronique, faute d'infrastructures d'irrigation adaptées. »
**Correction humaine** : le porteur a remplacé « chronique » par « saisonnier » car le manque d'eau n'est pas permanent.

### Prompt « Pitch »
```
Rédige un pitch de 4 phrases à partir de ce texte.

[texte du porteur]
```
**Résultat typique** : pitch structuré (problème → solution → impact → appel à l'action).
**Correction humaine** : le porteur a ajouté le nom de la localité cible, absent du pitch généré.

### Prompt « SWOT »
```
Propose une analyse SWOT courte (forces, faiblesses, opportunités, menaces).

[texte du porteur]
```
**Résultat typique** : tableau en 4 points. L'IA identifie correctement les forces et faiblesses à partir du texte fourni.
**Correction humaine** : ajout d'une menace spécifique (concurrence d'un projet similaire dans la région) que l'IA ne pouvait pas connaître.

---

## 2. Prompts utilisés pendant le développement

### 2.1 Architecture initiale
**Prompt** : « Concevoir une plateforme Django de gestion d'incubateur avec : dépôt de dossier, évaluation par comité, affectation de mentor, suivi des jalons avec alertes de retard, tableau de bord, exports PDF/Excel, assistant IA de rédaction. »

**Résultat** : structure complète du projet (models.py, views.py, forms.py, templates, urls.py, settings.py) générée en un seul passage.

**Corrections apportées** :
- Ajout du champ `genre` sur le modèle User (absent de la première version).
- Correction du `limit_choices_to={"role": "mentor"}` sur la ForeignKey mentor.
- Ajustement des couleurs CSS pour correspondre à la charte ISEP (tons marron/beige).

### 2.2 Commande seed
**Prompt** : « Créer une commande Django `seed` qui génère des données de démonstration réalistes : 4 comptes de test, 30 projets fictifs avec des noms sénégalais, des évaluations et des jalons. »

**Résultat** : commande fonctionnelle avec Random(42) pour la reproductibilité.

**Corrections apportées** :
- Ajout de la vérification `if User.objects.exists()` pour éviter les doublons.
- Diversification des prénoms sénégalais (Aminata, Omar, Khady, Samba, etc.).
- Ajout de jalons « Suivi à 3 mois » parmi les jalons générés.

### 2.3 Tests automatisés
**Prompt** : « Écrire des tests Django couvrant : CSRF, droits par rôle, dépôt, complétude, fichier interdit, évaluation, mentor, jalons, dashboard, exports, assistant IA. »

**Résultat** : 5 tests couvrant les parcours critiques.

**Corrections apportées** :
- Ajout de `@override_settings(MEDIA_ROOT=tempfile.mkdtemp())` pour isoler les fichiers de test.
- Correction du test IA pour utiliser `mock.patch.dict(os.environ)` afin de supprimer la clé API pendant le test.

### 2.4 Configuration Render
**Prompt** : « Générer un render.yaml pour déployer cette application Django sur Render avec le plan gratuit. »

**Résultat** : fichier YAML fonctionnel.

**Corrections apportées** :
- Séparation du buildCommand et du startCommand (initialement tout était dans startCommand).
- Ajout de `makemigrations incubateur` dans le build.
- Ajout de `generateValue: true` pour DJANGO_SECRET_KEY.

### 2.5 Amélioration du design
**Prompt** : « Refaire le CSS avec un design premium, Google Fonts Inter, variables CSS, animations, meilleur responsive mobile, en gardant les couleurs ISEP (tons marron/beige). »

**Résultat** : CSS complet avec variables, gradients, hover effects, animations fadeIn/slideIn.

**Corrections apportées** :
- Ajustement des breakpoints responsive (768px et 480px).
- Ajout de `position: sticky` sur le header.
- Réduction de la taille des polices sur mobile.

---

## 3. Observations sur l'utilisation de l'IA

### Points positifs
- **Accélération** : la structure du projet (modèles, vues, formulaires) a été générée rapidement.
- **Qualité des suggestions** : les prompts de reformulation et pitch produisent des textes exploitables.
- **Couverture des tests** : l'IA a proposé des cas de test auxquels on n'aurait pas pensé (fichier .exe, CSRF).

### Points de vigilance
- **Vérification systématique** : chaque code généré a été relu et testé avant intégration.
- **Faits inventés** : sans le garde-fou « sans inventer de faits », l'IA ajoutait parfois des statistiques fictives.
- **Contexte local** : l'IA ne connaît pas les spécificités du CIAT → les corrections humaines sont indispensables.
- **Dépendances** : certaines dépendances suggérées étaient mal versionnées → vérification dans requirements.txt.

### Conclusion
L'IA générative a été un **accélérateur** significatif à chaque étape du projet, mais la **vérification humaine** reste indispensable pour garantir la qualité, l'exactitude et l'adaptation au contexte local.
