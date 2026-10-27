# Guide utilisateur — Plateforme de gestion de l'incubateur du CIAT

## Accéder à la plateforme

**URL** : https://ciat-incubateur.onrender.com

La plateforme est accessible depuis un navigateur web (ordinateur ou téléphone). La première page affichée est l'écran de connexion.

---

## 1. Porteur de projet

### 1.1 Créer un compte
1. Sur la page de connexion, cliquer **« Pas de compte ? Créer un compte »**.
2. Remplir : nom complet, genre (facultatif), adresse e-mail, mot de passe (8 caractères minimum).
3. Cliquer **« Créer mon compte »** → redirection vers la page d'accueil.

### 1.2 Déposer un dossier
1. Cliquer **« 📁 Mon dossier »** dans la barre de navigation.
2. Cliquer **« + Déposer un dossier »**.
3. Remplir le formulaire :
   - **Titre** : nom court du projet.
   - **Domaine** : choisir parmi les 7 domaines du CIAT.
   - **Problème identifié** : décrire le besoin auquel le projet répond.
   - **Solution proposée** : décrire la solution envisagée.
   - **Pièce jointe** : document complémentaire (PDF, PNG, JPG, DOCX — 5 Mo max).
4. Cliquer **« Enregistrer »**. La jauge de complétude indique le pourcentage rempli.

### 1.3 Utiliser l'assistant IA
1. Cliquer **« 🤖 Assistant IA »** dans la navigation.
2. Saisir un texte brouillon dans le champ **« Mon texte »**.
3. Choisir un mode : **Reformuler**, **Pitch**, ou **SWOT**.
4. Cliquer **« Générer une suggestion »** → l'IA (ou le mode démo) propose un texte.
5. Modifier la suggestion si nécessaire.
6. Choisir le projet et le champ cible (Problème ou Solution).
7. Cliquer **« Valider et enregistrer »** → le texte est enregistré dans le dossier avec la mention « rédigé avec l'aide d'une IA ».

> **Important** : aucun texte n'est enregistré sans votre validation explicite.

### 1.4 Suivre son dossier
- La page du projet affiche le statut (Soumis, À compléter, Accepté, Refusé).
- Les évaluations du comité et les jalons sont visibles en lecture.
- Tant que le statut est « Soumis » ou « À compléter », le bouton **« Modifier »** permet de corriger le dossier.

### 1.5 Modifier son profil
1. Cliquer sur **« 👤 Votre nom »** dans la navigation.
2. Modifier le nom complet ou le genre.
3. Cliquer **« Enregistrer les modifications »**.

---

## 2. Membre du comité

### 2.1 Consulter les projets
1. Cliquer **« 📁 Projets »** → liste de tous les projets soumis.
2. Cliquer sur le titre d'un projet pour voir le détail.

### 2.2 Évaluer un projet
1. Sur la page d'un projet, remplir la grille de notation en bas de la section **« Évaluations »** :
   - **Innovation** (0-5), **Faisabilité** (0-5), **Impact** (0-5), **Équipe** (0-5).
   - **Décision** : Accepté, Refusé, ou À compléter.
   - **Motivation** : justification obligatoire.
2. Cliquer **« Enregistrer la décision »**.
3. Le statut du projet est automatiquement mis à jour.

### 2.3 Tableau de bord
- Cliquer **« 📊 Tableau de bord »** pour voir les statistiques globales.
- Utiliser les filtres (cohorte, domaine, statut) pour affiner la vue.

---

## 3. Mentor

### 3.1 Consulter les projets affectés
- Cliquer **« 📁 Projets »** → seuls les projets qui vous sont affectés apparaissent.

### 3.2 Gérer les jalons
1. Sur la page d'un projet, section **« Suivi et jalons »** :
   - **Ajouter un jalon** : renseigner le titre et la date d'échéance, cliquer « Ajouter ».
   - **Mettre à jour un jalon** : changer le statut (À faire → En cours → Validé), ajouter un commentaire, cliquer « OK ».
2. Les jalons en retard sont signalés en rouge.

---

## 4. Coordonnateur

Le coordonnateur a accès à **toutes les fonctionnalités** des autres rôles, plus :

### 4.1 Affecter un mentor
1. Sur la page d'un projet **accepté**, section « Suivi et jalons ».
2. Sélectionner un mentor dans la liste déroulante.
3. Cliquer **« Affecter »**.

### 4.2 Exporter les données
- **Export Excel** : cliquer **« 📥 Export Excel »** dans la navigation → télécharge un fichier `.xlsx` avec tous les projets.
- **Fiche PDF** : sur chaque page de projet, cliquer **« Fiche PDF »** pour télécharger une fiche individuelle.

### 4.3 Tableau de bord
- Vue complète avec indicateurs : nombre de dossiers, taux de sélection, jalons en retard, avancement global.
- Graphiques : répartition par domaine, par cohorte, par genre.

### 4.4 Administration
- Cliquer **« ⚙️ Administration »** pour accéder à Django Admin.
- Gérer les utilisateurs, projets, évaluations et jalons directement.

---

## Résolution de problèmes

| Problème | Solution |
|---|---|
| Mot de passe oublié | Contacter le coordonnateur, qui le réinitialise dans l'administration ; le changer ensuite dans « Mon profil » |
| « Trop de tentatives de connexion » | Attendre 15 minutes (protection après 5 essais erronés) |
| Fichier refusé | Vérifier l'extension (pdf, png, jpg, docx) et la taille (< 5 Mo) |
| Page « Accès interdit » (403) | Vous n'avez pas le rôle requis pour cette action |
| Le site met du temps à charger | Normal sur Render gratuit (réveil après 15 min d'inactivité) |
