# Schéma et dictionnaire de la base de données

## Diagramme Entité-Relation

```mermaid
erDiagram
    User ||--o{ Projet : "dépose (owner)"
    User ||--o{ Projet : "accompagne (mentor)"
    User ||--o{ Evaluation : "évalue"
    Projet ||--o{ Evaluation : "reçoit"
    Projet ||--o{ Jalon : "contient"

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
        string comment "Commentaire (300 car. max)"
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
| `comment` | CharField(300) | Facultatif | Commentaire du mentor ou coordonnateur |

**Propriété calculée :** `en_retard` = True si statut ≠ « validé » et échéance < aujourd'hui

## Relations et règles métier

1. Un **porteur** peut avoir plusieurs projets ; un projet appartient à un seul porteur.
2. Un **mentor** peut suivre plusieurs projets ; un projet a au plus un mentor.
3. L'affectation de mentor n'est possible que si le projet est **accepté**.
4. Un projet peut recevoir plusieurs **évaluations** ; chaque évaluation met à jour le statut.
5. Les **jalons** sont ordonnés par date d'échéance ; un retard est signalé automatiquement.
6. La suppression d'un utilisateur supprime ses projets (CASCADE) mais libère ses projets mentorés (SET_NULL).
