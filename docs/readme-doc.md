# CartoPharma - document de reference pour entretenir `README.md`

## 1. Objet du `README.md`

Le vrai `README.md` du depot a un role public et operationnel.

Il doit permettre, en quelques minutes, de comprendre :
- ce qu est CartoPharma ;
- ce que le projet fait vraiment aujourd hui ;
- comment lancer le projet ;
- quelles routes et quels composants structurants existent ;
- quelles sont les limites actuelles du projet.

Le `README.md` ne doit pas devenir une documentation exhaustive. Les details longs, les runbooks et les conventions UI restent dans `docs/`.

## 2. Role de `docs/readme-doc.md`

Ce fichier est la norme interne de maintenance du vrai `README.md`.

Il definit :
- la structure canonique du `README.md` ;
- les informations qui doivent y rester synchronisees ;
- les cas ou sa mise a jour est obligatoire ;
- les verifications a faire avant commit/push.

En cas de doute, ce document prime sur les habitudes locales.

## 3. Etat constate sur l archive analysee

Consigne stricte : le `README.md` doit decrire l etat reel du depot au commit courant, pas l etat suppose, pas l etat d une branche precedente, pas ce qui existe seulement dans le cache `.next/` ou dans `git show HEAD`.

## 4. Principes editoriaux du vrai `README.md`

Le `README.md` de CartoPharma doit rester :
- professionnel ;
- sobre ;
- lisible ;
- factuel ;
- court mais utile ;
- strictement coherent avec le code et les fichiers presents.

Regles editoriales :
- ecrire pour un lecteur humain qui decouvre le depot ;
- annoncer uniquement ce qui fonctionne ou ce qui est effectivement versionne ;
- distinguer clairement le disponible maintenant, le mocke, et le prevu plus tard ;
- preferer des formulations directes et calmes ;
- ne pas survendre le produit ;
- ne pas dupliquer la documentation detaillee de `docs/`.

## 5. Structure canonique du `README.md`

Ordre recommande et stable :

1. `# CartoPharma`
2. resume projet en 2 a 4 lignes
3. statut actuel / perimetre
4. fonctionnalites actuelles
5. structure du depot
6. stack technique
7. prerequis
8. installation / configuration
9. demarrage rapide
10. scripts utiles
11. Docker
12. routes principales
13. API principale
14. donnees et base de donnees
15. documentation disponible
16. limites actuelles / non inclus

Cet ordre ne doit etre modifie que si la lisibilite y gagne clairement.

## 6. Contenu obligatoire du `README.md` pour CartoPharma

### 6.1 Identite du projet

Le README doit toujours expliciter :
- le nom `CartoPharma` ;
- le perimetre France uniquement ;
- la finalite actuelle : application cartographique sante/services avec socle frontend/backend ;
- le statut fonctionnel reel du projet.

### 6.2 Resume projet

Le resume doit dire, sans blabla :
- qu il s agit d une application cartographique ;
- que le backend repose sur FastAPI ;
- qu une base SQLite est utilisee pour le runtime ;
- que la phase actuelle repose encore sur des couches et points mockes tant que les vraies donnees metier ne sont pas branchees.

### 6.3 Fonctionnalites

Le README doit decrire uniquement les fonctionnalites observables a la date du commit. Pour CartoPharma, cela veut dire au minimum :
- exposition d une API versionnee ;
- endpoint de statut et de sante ;
- catalogue de couches cartographiques ;
- points cartographiques GeoJSON/mockes ;
- persistance SQLite des settings d affichage.

Si le frontend applicatif est bien present dans le depot, ajouter aussi :
- page d accueil `/` ;
- page carte `/map` ;
- page parametres `/settings` ;
- carte Leaflet ;
- panneau d activation/desactivation des couches.

### 6.4 Structure du projet

Le README doit presenter la structure reelle du depot, pas une structure ideale.

Structure a documenter tant qu elle existe :
- `backend/` : API FastAPI, schemas, routes, acces SQLite ;
- `data/` : base SQLite, logs et fichiers runtime ;
- `docs/` : documentation interne ;
- `Dockerfile` : image applicative ;
- `frontend/` : uniquement si le code source ou les fichiers de build necessaires sont vraiment presentes.

Ne pas documenter comme structure normale :
- `.venv/` ;
- `frontend/node_modules/` ;
- `frontend/.next/` ;
- `__pycache__/` ;
- fichiers purement locaux ou caches.

### 6.5 Stack technique

La section stack doit rester synchronisee avec les manifests reels.

Aujourd hui, la documentation doit partir de :
- backend : FastAPI, Uvicorn, Pydantic (`backend/requirements.txt`) ;
- base de donnees : SQLite (`backend/app/db/database.py`, `data/cartopharma.sqlite`) ;
- Docker : image Node + Python via `Dockerfile` ;
- frontend : Next.js App Router, React, React Query, Leaflet, Tailwind v4 seulement si `frontend/package.json` est present dans l arbre de travail.

Si `frontend/package.json` n est pas versionne au commit, le README ne doit pas afficher une stack frontend detaillee basee uniquement sur des souvenirs, sur `node_modules/`, ou sur des artefacts `.next/`.

### 6.6 Prerequis

Le README doit mentionner uniquement les prerequis reels necessaires au lancement de l etat courant :
- Python 3 pour le backend ;
- Node.js/npm uniquement si le frontend source et son manifest sont presents ;
- Docker uniquement si la section Docker est conservee et testee.

### 6.7 Installation et demarrage rapide

Le README doit proposer des commandes qui fonctionnent vraiment.

Règles :
- documenter les scripts racine seulement s ils existent au commit (`run_linux.sh`, `run_win.bat`, `start_backend.bat`, `start_frontend.bat`) ;
- documenter un lancement manuel backend si les scripts ne sont pas presents ;
- documenter le lancement frontend uniquement si le frontend versionne est effectivement lancable ;
- ne jamais laisser dans le README une commande non testee ou pointant vers un fichier supprime.

### 6.8 Docker

La section Docker est obligatoire uniquement si `Dockerfile` est conserve.

Pour CartoPharma, elle doit rester coherente avec le vrai `Dockerfile` :
- build frontend dans un stage Node ;
- image finale Node + Python ;
- variable `CARTOPHARMA_DATA_DIR=/data` ;
- variable `CARTOPHARMA_MODE=docker` ;
- exposition du port `3000` ;
- lancement via `/app/run_linux.sh --docker`.

Si `run_linux.sh` ou `frontend/package.json` sont absents, la section Docker doit etre revue avant chaque commit ; sinon elle devient mensongere.

### 6.9 Routes et API

Le README doit separer clairement :
- les routes frontend ;
- les endpoints backend.

Cote backend, la base actuelle a documenter provient de :
- `GET /`
- `GET /health`
- `GET /api/v1/health`
- `GET /api/v1/settings`
- `PATCH /api/v1/settings`
- `GET /api/v1/layers`
- `GET /api/v1/layers/points`

Cote frontend, ne documenter `/`, `/map`, `/settings` que si ces routes existent vraiment dans le code versionne ou, a defaut, si elles sont explicitement conservees comme comportement livre avec les fichiers du commit.

### 6.10 Configuration

Le README doit lister uniquement les variables qui ont un impact reel :
- `CARTOPHARMA_DATA_DIR`
- `CARTOPHARMA_DATABASE_URL`
- `CARTOPHARMA_CORS_ORIGINS`
- `NEXT_PUBLIC_API_URL` si `frontend/.env.example` et le frontend sont actifs ;
- `INTERNAL_API_URL` si le proxy Next.js est encore utilise.

### 6.11 Donnees et base de donnees

Le README doit rappeler :
- que la base par defaut est `data/cartopharma.sqlite` ;
- que les logs backend sont ecrits dans `data/logs/` ;
- que `data/layers/` et `data/tmp/` sont des repertoires runtime ;
- que les points exposes sont actuellement mockes tant que l indexation metier n est pas branchee.

### 6.12 Documentation disponible

Le README doit pointer seulement vers les documents encore utiles et presents, par exemple :
- `docs/style-frontend-ui.md`
- `docs/metrics_catalog.md`
- `docs/ROADMAP.md`
- `docs/documentation_update_runbook.md`
- `docs/indexation.md`
- `docs/indexation_operational_runbook.md`

### 6.13 Statut et roadmap

Le README doit distinguer :
- ce qui est termine ;
- ce qui est en cours ;
- ce qui est hors perimetre.

Pour CartoPharma, ne pas presenter comme deja disponible :
- les vraies donnees pharmacies ;
- les calculs de zone de chalandise ;
- les pipelines d ingestion massifs ;
- une CI/CD si aucun pipeline versionne n est visible.

## 7. Contenu optionnel

Sections autorisees uniquement si elles sont justifiees par le depot :
- captures d ecran ;
- roadmap detaillee ;
- statut CI/CD ;
- conventions de contribution ;
- FAQ courte.

Sections a eviter par defaut :
- historique detaille des changements ;
- documentation UI exhaustive ;
- schemas d architecture trop longs ;
- catalogue integral de l API si `docs/metrics_catalog.md` existe deja.

## 8. Regles de style Markdown

Le vrai `README.md` doit respecter ces regles :
- un seul titre H1 ;
- H2 pour les sections principales ;
- H3 seulement si necessaire ;
- pas d emojis decoratifs ;
- pas de ton marketing ;
- pas de paragraphes trop longs ;
- pas de listes de plus de 6 a 8 points sans raison ;
- pas de sections vides ;
- pas de doubles informations a deux endroits differents ;
- fences de code typées (`bash`, `powershell`, `json`) ;
- noms de fichiers et de dossiers ecrits en inline code.

Regles de lisibilite :
- introduire chaque section par une phrase utile ;
- preferer une liste courte plutot qu un bloc dense ;
- garder un ordre stable d une version a l autre ;
- supprimer toute phrase qui n aide ni a comprendre ni a lancer le projet.

## 9. Regles de synchronisation avec le projet reel

Avant toute mise a jour du `README.md`, verifier ces sources de verite :

| Sujet | Source de verite principale | Verification attendue |
|---|---|---|
| nom et version API | `backend/app/core/config.py` | `APP_NAME`, `APP_VERSION` |
| routes backend | `backend/app/main.py`, `backend/app/api/router.py`, `backend/app/api/routes/*.py` | routes exactes et methodes HTTP |
| stack backend | `backend/requirements.txt` | bibliotheques reellement declarees |
| structure frontend | `frontend/src/` et `frontend/package.json` | ne documenter que ce qui est versionne |
| routes frontend | `frontend/src/app/**` ou a defaut manifests `.next` | verifier que le code source existe encore |
| variables d environnement | `backend/app/core/config.py`, `frontend/.env.example`, `frontend/next.config.ts` | noms exacts et usage reel |
| donnees runtime | `data/`, `backend/app/db/database.py` | base SQLite, logs, dossiers runtime |
| Docker | `Dockerfile` | build, ports, entrypoint, prerequis |
| docs reliees | `docs/*.md` | liens encore valides |
| scripts de lancement | fichiers racine `*.bat` / `*.sh` | presence reelle dans l arbre de travail |

Regle specifique a ce depot :
- toujours lancer `git status --short` avant de mettre a jour le README ;
- si des fichiers references par le README sont marques `D` ou absents, il faut soit les restaurer, soit nettoyer immediatement le README.

## 10. Cas imposant une mise a jour obligatoire du `README.md`

La mise a jour du vrai `README.md` est obligatoire si l un des points suivants change :
- ajout ou suppression d une fonctionnalite visible ;
- ajout, suppression ou renommage d une route frontend (`/`, `/map`, `/settings`, autres) ;
- ajout, suppression ou modification d un endpoint backend ;
- changement de schema des settings ou des couches ;
- changement de base de donnees ou de chemin par defaut ;
- changement des variables d environnement ;
- changement des scripts de lancement ;
- changement du `Dockerfile` ou du mode d execution Docker ;
- changement de la structure de dossiers exposee dans le README ;
- ajout de documentation importante dans `docs/` ;
- changement de nom, de version, de perimetre geographique ou de statut produit ;
- passage de donnees mockees a des donnees reelles ;
- ajout d une CI/CD reelle ou suppression d une pipeline existante.

## 11. Erreurs frequentes a eviter

Pour CartoPharma, les erreurs les plus probables sont :
- documenter des scripts supprimes du depot ;
- annoncer une stack frontend detaillee alors que `frontend/package.json` est absent ;
- confondre ce qui existe dans `git HEAD` avec ce qui existe dans l arbre de travail actuel ;
- confondre donnees mockees et donnees metier reelles ;
- oublier la contrainte `France uniquement` ;
- oublier le stockage SQLite des settings ;
- dupliquer dans le README le contenu complet de `docs/style-frontend-ui.md` ou `docs/metrics_catalog.md` ;
- documenter `.next/`, `node_modules/` ou `.venv/` comme des parties normales du projet ;
- laisser une section Docker sans verifier que la chaine complete build + run fonctionne encore ;
- presenter une CI/CD inexistante ;
- garder des liens vers des documents supprimes ;
- laisser des formulations vagues du type `architecture scalable` sans preuve concrete dans le depot.

## 12. Checklist de validation avant commit/push

Avant de considerer le `README.md` comme a jour :

### 12.1 Verification structurelle
- [ ] `README.md` existe a la racine.
- [ ] `docs/readme-doc.md` reste coherent avec la structure attendue.
- [ ] le README suit l ordre canonique defini dans ce document.
- [ ] aucune section vide ou obsolete n est conservee.

### 12.2 Verification de coherence depot
- [ ] `git status --short` a ete verifie.
- [ ] chaque fichier, route, script ou commande mentionne existe reellement.
- [ ] les references a `frontend/package.json`, `frontend/src/` et aux scripts racine ont ete revalidees.
- [ ] les fichiers caches ou locaux ne sont pas presentes comme des composants projet.

### 12.3 Verification fonctionnelle minimale
- [ ] les endpoints backend documentes correspondent au code FastAPI.
- [ ] la base par defaut et les dossiers runtime documentes correspondent au code backend.
- [ ] les variables d environnement documentees existent vraiment.
- [ ] la section Docker correspond au `Dockerfile` courant.
- [ ] si des scripts de lancement sont cites, ils ont ete verifies.

### 12.4 Verification redactionnelle
- [ ] le ton est sobre et professionnel.
- [ ] le README reste court et actionnable.
- [ ] aucune promesse produit n anticipe une roadmap non livree.
- [ ] aucune information detaillee deja mieux traitee dans `docs/` n est recopies inutilement.
- [ ] les commandes copiable-collable sont propres.

## 13. Regle de maintenance continue

Apres chaque changement de code ou de structure :
1. verifier si le changement impacte une section du `README.md` ;
2. mettre a jour le README dans le meme commit que le changement ;
3. relire `docs/documentation_update_runbook.md` pour les autres docs impactees ;
4. verifier que `README.md` et `docs/readme-doc.md` restent alignes.

Pour CartoPharma, la regle est simple : si le lecteur ne peut pas retrouver dans le depot ce que promet le `README.md`, alors le README est faux et doit etre corrige avant merge.
