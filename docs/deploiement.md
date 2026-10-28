# Déploiement en production — Render + Neon + Cloudflare R2

L'application tourne sur **Render** (serveur web), enregistre ses données dans **Neon** (PostgreSQL) et
les fichiers déposés dans **Cloudflare R2** (bucket privé). Les trois offres sont gratuites. Contrairement
au disque de Render, Neon et R2 **conservent** les données entre deux redéploiements.

> Ne jamais écrire une clé, un mot de passe ou une chaîne de connexion dans le code, dans un document
> ou dans un message : uniquement dans l'onglet **Environment** de Render.

## 1. Base de données Neon

1. Sur https://console.neon.tech, créer un projet `ciat-incubateur` (PostgreSQL 16, région **Europe**,
   par exemple Frankfurt, proche du serveur Render).
2. Dans **Connection details**, copier la chaîne de connexion de la branche principale. Elle a la forme
   `postgresql://utilisateur:motdepasse@ep-xxxx.eu-central-1.aws.neon.tech/neondb?sslmode=require`.
   Elle servira pour `DATABASE_URL`.

## 2. Stockage des fichiers Cloudflare R2

1. Sur le tableau de bord Cloudflare, **R2 Object Storage** > **Create bucket** : nom `ciat-incubateur-fichiers`,
   accès public **désactivé**. Le bucket reste privé : les fichiers ne sont servis que par l'application,
   après vérification des droits.
2. **Manage R2 API Tokens** > **Create API token** : permission **Object Read & Write**, limitée à ce bucket.
3. Noter :
   - l'**Access Key ID** → `R2_ACCESS_KEY_ID` ;
   - le **Secret Access Key** → `R2_SECRET_ACCESS_KEY` (affiché une seule fois) ;
   - l'adresse **S3 API** du bucket (R2 > bucket > **Settings**), **sans** le `/nom-du-bucket` final → `R2_ENDPOINT`.
     Exemple de forme : `https://3f2a…(32 caractères)….r2.cloudflarestorage.com`. Ne pas recopier `<ACCOUNT_ID>` :
     c'est l'emplacement de l'identifiant de votre compte Cloudflare. Une adresse mal formée est signalée dans le journal
     Render au démarrage (« R2_ENDPOINT invalide »).

## 3. Variables d'environnement sur Render

Service `ciat-incubateur` > **Environment** :

| Variable | Valeur |
|---|---|
| `DATABASE_URL` | chaîne de connexion Neon |
| `R2_BUCKET` | `ciat-incubateur-fichiers` |
| `R2_ENDPOINT` | adresse « S3 API » du bucket, sans le nom du bucket : `https://` + identifiant de compte (32 caractères) + `.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | clés du jeton R2 |
| `CIAT_ADMIN_EMAIL` | e-mail du coordonnateur réel |
| `CIAT_ADMIN_PASSWORD` | mot de passe fort (12 caractères ou plus), à changer après la première connexion |
| `CIAT_ADMIN_NOM` | nom affiché, par exemple « Coordination CIAT » |
| `SEED_DEMO` | `1` : créer les comptes de démonstration du jury ; `supprimer` : les retirer ; `0` : rien |
| `DEMO_PASSWORD` | mot de passe commun des comptes de démonstration, communiqué au jury seulement |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_SECRET_KEY` | longue valeur aléatoire (bouton **Generate**) |
| `GROQ_API_KEY` | clé Groq gratuite pour l'assistant IA (voir § 6) ; sans clé, mode démonstration |
| `ANTHROPIC_API_KEY`, `IA_FOURNISSEUR` | facultatif : Claude à la place de Groq (voir § 6) |

Dans **Settings** > **Build Command**, mettre : `bash build.sh`. Commande de démarrage : `gunicorn config.wsgi`.

## 4. Mise en ligne

Au déploiement suivant, `build.sh` :

1. installe les dépendances et prépare les fichiers statiques ;
2. applique les migrations sur Neon (`migrate`) — les migrations sont créées en local et versionnées ;
3. crée le compte coordonnateur réel s'il n'existe pas (`init_coordo`) ;
4. si `SEED_DEMO=1`, crée une seule fois les comptes et les 30 projets de démonstration (`seed`).

Vérifications après le déploiement :

- se connecter avec `CIAT_ADMIN_EMAIL` et ouvrir `/admin/` ;
- déposer un document sur un projet, redéployer (**Manual Deploy**), vérifier qu'il est toujours téléchargeable ;
- se connecter avec un compte de démonstration : `/admin/` doit être refusé.

## 5. Exploitation

- **Créer un mentor ou un membre du comité** : `/admin/` > Utilisateurs > Ajouter. L'identifiant est l'e-mail ;
  choisir le rôle et un mot de passe provisoire, que la personne changera depuis **Mon profil**.
- **Mot de passe du coordonnateur perdu ou refusé** : ajouter `CIAT_ADMIN_RESET=1` dans Render (et vérifier
  `CIAT_ADMIN_PASSWORD`), laisser le redéploiement se faire, se connecter, puis **supprimer** `CIAT_ADMIN_RESET`.
  Après 5 essais erronés, la connexion est bloquée 15 minutes (un redéploiement lève aussi le blocage).
- **Mot de passe oublié** : le coordonnateur le réinitialise dans `/admin/` (fiche de l'utilisateur > formulaire
  « mot de passe »).
- **Retirer la démonstration** après l'évaluation : mettre `SEED_DEMO` à `supprimer` et redéployer
  (comptes et projets fictifs supprimés), puis le remettre à `0`. Les comptes réels ne sont pas touchés.
- **Sauvegardes** : Neon conserve un historique de restauration (quelques heures à quelques jours sur
  l'offre gratuite, voir la console Neon). Pour une sauvegarde complète :
  `pg_dump "$DATABASE_URL" > sauvegarde.sql`.
- **Mise en veille** : sur l'offre gratuite, Render endort le service après 15 minutes sans visite ; la première
  page met alors 30 à 60 secondes à s'afficher. Les données ne sont pas perdues.
- **Limites anti-abus** : 5 échecs de connexion (par e-mail ou par adresse IP) bloquent la connexion 15 minutes ;
  20 appels à l'IA par utilisateur et par heure.

## 6. Assistant IA : clé Groq (gratuite)

Par défaut, l'assistant utilise **Groq**, dont l'offre gratuite suffit au volume du CIAT, avec le modèle ouvert
`openai/gpt-oss-120b`.

1. Créer un compte sur https://console.groq.com (pas de carte bancaire pour l'offre gratuite).
2. **API Keys > Create API Key** : nommer la clé `ciat-incubateur-render`, la copier (affichée une seule fois).
3. Sur Render, **Environment** : ajouter `GROQ_API_KEY` avec cette valeur, puis enregistrer (redéploiement).
4. Vérifier : en porteur, ouvrir **Assistant IA** et générer une suggestion. La mention « Générée par l'IA » confirme
   l'appel réel ; « mode démonstration » signifie que la clé est absente ou refusée. Le journal Render en indique la
   raison : « clé GROQ_API_KEY refusée », « limite gratuite Groq atteinte », « API Groq injoignable ».

Limites de l'offre gratuite pour `openai/gpt-oss-120b` (octobre 2026, partagées par toute l'organisation Groq) :
30 requêtes par minute, 1 000 par jour, 8 000 jetons par minute, 200 000 par jour. Une suggestion consomme environ
1 000 à 2 000 jetons. En plus, la plateforme limite chaque utilisateur à 20 demandes par heure.

Variables facultatives : `GROQ_MODEL` (autre modèle Groq, par exemple `openai/gpt-oss-20b`, plus rapide) et
`GROQ_EFFORT` (`low`, `medium` par défaut, `high`).

**Option payante : Claude.** Avec `ANTHROPIC_API_KEY` (clé créée sur https://platform.claude.com, avec crédits et
limite de dépense) et `IA_FOURNISSEUR=anthropic`, l'assistant utilise `claude-opus-5` (modifiable par `ANTHROPIC_MODEL`).
Sans `IA_FOURNISSEUR`, Groq est prioritaire dès que `GROQ_API_KEY` est définie.

Ne jamais coller une clé dans le code, un document, un message ou une capture d'écran. Si elle a été exposée,
la supprimer dans la console du fournisseur et en créer une nouvelle.
