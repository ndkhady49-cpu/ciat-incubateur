# Schéma et dictionnaire de la base de données

## Diagramme Entité-Relation

```mermaid
erDiagram
    User ||--o{ Projet : "dépose (owner)"
    User ||--o{ Projet : "accompagne (mentor)"
    User ||--o{ Evaluation : "évalue"
    Projet ||--o{ Evaluation : "reçoit"
    Projet ||--o{ Jalon : "contient"
    Projet ||--o{ Document : "documents du dossier"
    Jalon ||--o{ Document : "preuves"
    Projet ||--o{ Commentaire : "échanges"
    Jalon ||--o{ Commentaire : "commentaires"
    Projet ||--o{ Suivi : "suivis 3 et 6 mois"
    Projet ||--o{ CompteRendu : "comptes rendus"

    User {
        int id PK
        string username "E-mail (identifiant unique)"
        string email "Adresse e-mail"
        string password "Mot de passe hashé"
        string first_name "Nom complet"
        string role "porteur | comite | mentor | coordo"
        string genre "Femme | Homme | vide"
        datetime date_joined "Date d'inscription"
        bool is_staff "Accès admin"
    }

    Projet {
        int id PK
        int owner_id FK "Porteur (User)"
        string title "Titre du projet (200 car.)"
        string domain "Domaine d'intervention"
        text problem "Problème identifié"
        text solution "Solution proposée"
        string cohort "Cohorte (ex: 2026-A)"
        string status "soumis | a_completer | accepte | refuse"
        file file "Pièce jointe (pdf/png/jpg/docx, 5 Mo max)"
        int mentor_id FK "Mentor affecté (User, nullable)"
        text objectifs "Objectifs d'accompagnement"
        date fin_incubation "Fin d'incubation (nullable)"
        bool ia_used "Texte généré avec IA"
        date created "Date de création"
    }

    Evaluation {
        int id PK
        int project_id FK "Projet évalué"
        int evaluator_id FK "Évaluateur (User)"
        int innovation "Note 0-5"
        int faisabilite "Note 0-5"
        int impact "Note 0-5"
        int equipe "Note 0-5"
        string decision "a_completer | accepte | refuse"
        text motivation "Justification de la décision"
        date created "Date de l'évaluation"
    }

    Jalon {
        int id PK
        int project_id FK "Projet concerné"
        string title "Titre du jalon (200 car.)"
        date due "Date d'échéance"
        string status "a_faire | en_cours | valide"
    }

    Document {
        int id PK
        int project_id FK "Projet"
        int jalon_id FK "Jalon prouvé (nullable)"
        string titre "Intitulé (150 car.)"
        file fichier "pdf/png/jpg/docx/xlsx, 5 Mo max"
        int auteur_id FK "Déposant (User)"
        datetime created "Date de dépôt"
    }

    Commentaire {
        int id PK
        int project_id FK "Projet"
        int jalon_id FK "Jalon commenté (nullable)"
        int auteur_id FK "Auteur (User)"
        text texte "1000 car. max"
        datetime created "Date"
    }

    Suivi {
        int id PK
        int project_id FK "Projet"
        int periode "3 | 6 (mois)"
        string situation "active | croissance | pause | arret"
        int emplois "Emplois créés"
        int chiffre_affaires "FCFA (nullable)"
        text observations "Observations"
        int auteur_id FK "Saisi par (User)"
        date created "Date de saisie"
    }

    CompteRendu {
        int id PK
        int project_id FK "Projet"
        int auteur_id FK "Rédacteur (User)"
        text texte "Contenu validé"
        bool ia_used "Brouillon généré par IA"
        datetime created "Date"
    }
```

## Dictionnaire des données

### Table `User` (extends AbstractUser)
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK, auto-incrémenté | Identifiant unique |
| `username` | CharField(150) | Unique, obligatoire | E-mail utilisé comme identifiant |
| `email` | EmailField | — | Adresse e-mail |
| `password` | CharField | Hashé (PBKDF2) | Mot de passe sécurisé |
| `first_name` | CharField(150) | — | Nom complet de l'utilisateur |
| `role` | CharField(10) | Choix : porteur, comite, mentor, coordo | Rôle déterminant les droits d'accès |
| `genre` | CharField(10) | Choix : Femme, Homme, vide | Genre (statistiques) |
| `is_staff` | BooleanField | Défaut : False | Accès à l'interface admin |
| `date_joined` | DateTimeField | Auto | Date de création du compte |

### Table `Projet`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `owner_id` | ForeignKey(User) | CASCADE, obligatoire | Porteur du projet |
| `title` | CharField(200) | Obligatoire | Titre du projet |
| `domain` | CharField(100) | Choix parmi 7 domaines CIAT | Domaine d'intervention |
| `problem` | TextField | Facultatif | Description du problème identifié |
| `solution` | TextField | Facultatif | Description de la solution proposée |
| `cohort` | CharField(20) | Défaut : « 2026-A » | Cohorte d'incubation |
| `status` | CharField(12) | Choix : soumis, a_completer, accepte, refuse | Statut courant du dossier |
| `file` | FileField | Extensions : pdf, png, jpg, jpeg, docx ; 5 Mo max | Pièce jointe |
| `mentor_id` | ForeignKey(User) | SET_NULL, nullable, rôle=mentor | Mentor affecté |
| `objectifs` | TextField | Facultatif | Objectifs d'accompagnement fixés par le mentor ou le coordonnateur |
| `fin_incubation` | DateField | Nullable | Fin d'incubation ; fixe les échéances des suivis (+90 et +180 jours) |
| `ia_used` | BooleanField | Défaut : False | Indique si l'IA a été utilisée |
| `created` | DateField | Défaut : date du jour | Date de création du dossier |

### Table `Evaluation`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `project_id` | ForeignKey(Projet) | CASCADE | Projet évalué |
| `evaluator_id` | ForeignKey(User) | CASCADE | Membre du comité ayant évalué |
| `innovation` | PositiveSmallIntegerField | 0 ≤ valeur ≤ 5 | Note d'innovation |
| `faisabilite` | PositiveSmallIntegerField | 0 ≤ valeur ≤ 5 | Note de faisabilité |
| `impact` | PositiveSmallIntegerField | 0 ≤ valeur ≤ 5 | Note d'impact |
| `equipe` | PositiveSmallIntegerField | 0 ≤ valeur ≤ 5 | Note de l'équipe |
| `decision` | CharField(12) | Choix : a_completer, accepte, refuse | Décision prise |
| `motivation` | TextField | Obligatoire | Justification de la décision |
| `created` | DateField | Défaut : date du jour | Date de l'évaluation |

**Propriété calculée :** `total` = innovation + faisabilité + impact + équipe (sur 20)

### Table `Jalon`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `project_id` | ForeignKey(Projet) | CASCADE | Projet concerné |
| `title` | CharField(200) | Obligatoire | Titre du jalon |
| `due` | DateField | Obligatoire | Date d'échéance |
| `status` | CharField(10) | Choix : a_faire, en_cours, valide | État d'avancement |

**Propriété calculée :** `en_retard` = True si statut ≠ « validé » et échéance < aujourd'hui

### Table `Document`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `project_id` | ForeignKey(Projet) | CASCADE | Projet concerné |
| `jalon_id` | ForeignKey(Jalon) | CASCADE, nullable | Vide : document du dossier ; renseigné : preuve du jalon |
| `titre` | CharField(150) | Obligatoire | Intitulé du document |
| `fichier` | FileField | Extensions : pdf, png, jpg, jpeg, docx, xlsx ; 5 Mo max | Fichier (téléchargement protégé par rôle) |
| `auteur_id` | ForeignKey(User) | CASCADE | Personne ayant déposé le fichier |
| `created` | DateTimeField | Automatique | Date de dépôt |

### Table `Commentaire`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `project_id` | ForeignKey(Projet) | CASCADE | Projet concerné |
| `jalon_id` | ForeignKey(Jalon) | CASCADE, nullable | Vide : échange général ; renseigné : commentaire du jalon |
| `auteur_id` | ForeignKey(User) | CASCADE | Auteur |
| `texte` | TextField | Obligatoire, 1000 car. max | Contenu |
| `created` | DateTimeField | Automatique | Date et heure |

### Table `Suivi`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `project_id` | ForeignKey(Projet) | CASCADE ; unique avec `periode` | Projet suivi |
| `periode` | PositiveSmallIntegerField | Choix : 3, 6 | Suivi à 3 ou 6 mois après la fin d'incubation |
| `situation` | CharField(12) | Choix : active, croissance, pause, arret | Situation du projet |
| `emplois` | PositiveSmallIntegerField | ≥ 0 | Emplois créés |
| `chiffre_affaires` | PositiveIntegerField | Nullable | Chiffre d'affaires en FCFA |
| `observations` | TextField | Facultatif | Observations du mentor ou coordonnateur |
| `auteur_id` | ForeignKey(User) | CASCADE | Personne ayant saisi le suivi |
| `created` | DateField | Défaut : date du jour | Date de saisie |

### Table `CompteRendu`
| Champ | Type | Contraintes | Description |
|---|---|---|---|
| `id` | BigAutoField | PK | Identifiant unique |
| `project_id` | ForeignKey(Projet) | CASCADE | Projet concerné |
| `auteur_id` | ForeignKey(User) | CASCADE | Rédacteur (mentor ou coordonnateur) |
| `texte` | TextField | Obligatoire | Texte relu et validé |
| `ia_used` | BooleanField | Défaut : False | Brouillon produit par l'IA puis validé par un humain |
| `created` | DateTimeField | Automatique | Date d'enregistrement |

## Relations et règles métier

1. Un **porteur** peut avoir plusieurs projets ; un projet appartient à un seul porteur.
2. Un **mentor** peut suivre plusieurs projets ; un projet a au plus un mentor.
3. L'affectation de mentor n'est possible que si le projet est **accepté**.
4. Un projet peut recevoir plusieurs **évaluations** ; chaque évaluation met à jour le statut.
5. Les **jalons** sont ordonnés par date d'échéance ; un retard est signalé automatiquement.
6. La suppression d'un utilisateur supprime ses projets (CASCADE) mais libère ses projets mentorés (SET_NULL).
7. Un **suivi** n'est saisi qu'une fois par période (3 ou 6 mois) ; il est signalé « dû » sur le tableau de bord
   dès que son échéance (fin d'incubation + 90 ou 180 jours) est passée.
8. Une **preuve** est un `Document` rattaché à un jalon du même projet ; la vue refuse un jalon d'un autre projet.
9. Un **compte rendu** n'est enregistré qu'après relecture : le brouillon de l'IA n'est jamais sauvegardé tel quel.
