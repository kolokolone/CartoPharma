# CartoPharma

CartoPharma est une application web de cartographie sante/services pour la France.
Le depot contient un backend FastAPI, un frontend Next.js et une base SQLite runtime. Le socle reste sobre, mais il sait maintenant reconstruire une couche `pharmacies` enrichie depuis un lot CSV metier, tout en conservant un fallback mock pour les couches non alimentees.

## Statut actuel

- version courante : `0.1.3`
- perimetre : France uniquement
- socle fonctionnel disponible : frontend, backend, carte Leaflet, couches activables, settings persistants
- indexation metier disponible : lot pharmacie specialise + projection cartographique enrichie

## Fonctionnalites actuelles

- API FastAPI versionnee sous `/api/v1`
- endpoints de statut et de sante
- catalogue de couches cartographiques
- exposition de points GeoJSON avec champs metier pharmacie (`pharmacist_count`, `pharmacy_establishment_id`, `pharmacy_type`)
- pipeline POI CSV -> SQLite dedie avec index spatial RTree
- import specialise des pharmacies depuis `data/csv/pharmacies/*.csv`
- endpoint de reindexation backend `POST /api/v1/indexing/rebuild-poi`
- endpoint de detail pharmacie `GET /api/v1/pharmacies/{establishment_id}`
- persistance SQLite des settings d affichage
- page d accueil `/`
- page carte `/map`
- page parametres `/settings` avec relance de la reindexation POI
- carte Leaflet avec panneau d activation/desactivation des couches

## Structure du depot

- `backend/` : API FastAPI, schemas, routes, acces SQLite
- `frontend/` : application Next.js App Router
- `data/` : base SQLite, logs et fichiers runtime
- `data/csv/` : depot des CSV POI bruts pour l import offline
- `docs/` : documentation interne et runbooks
- `Dockerfile` : build applicatif pour execution conteneurisee

## Stack technique

- backend : FastAPI, Uvicorn, Pydantic
- base de donnees : SQLite
- frontend : Next.js, React, React Query, Leaflet, Tailwind CSS v4
- conteneurisation : Docker (image Node + Python)

## Prerequis

- Python 3
- Node.js + npm
- Docker si vous utilisez le build conteneur

## Installation / configuration

Variables utiles :

- `CARTOPHARMA_DATA_DIR`
- `CARTOPHARMA_DATABASE_URL`
- `CARTOPHARMA_CORS_ORIGINS`
- `NEXT_PUBLIC_API_URL`
- `INTERNAL_API_URL`

Par defaut, la base runtime est creee dans `data/cartopharma.sqlite`.

## Demarrage rapide

### Windows

```bat
run_win.bat
```

### Backend seul

```bat
start_backend.bat
```

### Frontend seul

```bat
start_frontend.bat
```

### Linux / macOS

```bash
./run_linux.sh --dev
```

## Scripts utiles

- `run_win.bat` : lance backend + frontend sur Windows
- `run_win.bat --smoke` : verifie les prerequis essentiels
- `start_backend.bat` : lance uniquement le backend
- `start_frontend.bat` : lance uniquement le frontend
- `run_linux.sh --dev` : lance le projet en mode dev
- `run_linux.sh --docker` : mode runtime conteneur

## Docker

Le `Dockerfile` construit le frontend dans un stage Node, puis assemble une image finale Node + Python.

```bash
docker build -t cartopharma .
docker run --rm -p 3000:3000 -v ${PWD}/data:/data cartopharma
```

Le runtime conteneur utilise :

- `CARTOPHARMA_DATA_DIR=/data`
- `CARTOPHARMA_MODE=docker`
- port expose `3000`
- lancement via `/app/run_linux.sh --docker`

## Routes principales

Routes frontend :

- `/`
- `/map`
- `/settings`

## API principale

- `GET /`
- `GET /health`
- `GET /api/v1/health`
- `GET /api/v1/settings`
- `PATCH /api/v1/settings`
- `POST /api/v1/indexing/rebuild-poi`
- `GET /api/v1/layers`
- `GET /api/v1/layers/points`
- `GET /api/v1/pharmacies/{establishment_id}`

## Donnees et base de donnees

- base par defaut : `data/cartopharma.sqlite`
- base POI dediee : `data/poi.sqlite`
- logs backend : `data/logs/`
- repertoires runtime : `data/layers/`, `data/tmp/`
- projection pharmacie : `pharmacy_establishment`, `pharmacist`, `pharmacist_activity`, `pharmacist_degree` + projection dans `poi`
- points exposes : couches mixtes entre projection reelle et fallback mock selon les donnees disponibles

## Pipeline POI MVP

- le schema POI est initialise dans `data/poi.sqlite`
- les CSV bruts génériques sont lus depuis `data/csv/` et le lot pharmacie depuis `data/csv/pharmacies/`
- le script `python backend/scripts/build_poi_database.py` construit la base POI, recharge la projection pharmacie et reconstruit l index spatial
- l API `/api/v1/layers/points` accepte maintenant `bbox=minLon,minLat,maxLon,maxLat`
- le fichier legacy `data/csv/pharmacies.csv` n'est plus utilisé comme source métier pharmacie
- si `poi.sqlite` ne contient aucune couche active, le backend conserve un fallback mock

## Documentation disponible

- `docs/style-frontend-ui.md`
- `docs/metrics_catalog.md`
- `docs/ROADMAP.md`
- `docs/documentation_update_runbook.md`
- `docs/indexation.md`
- `docs/indexation_operational_runbook.md`
- `docs/importations_donnees.md`
- `docs/readme-doc.md`
- `docs/github-push.md`

## Limites actuelles

- geocodage adresse complet non inclus : les pharmacies sans coordonnees restent en attente
- pas de calcul de zone de chalandise
- pas encore de page frontend `/pharmacie/[id]`
- les autres couches restent encore largement en base mockee pour la V1 fondation
