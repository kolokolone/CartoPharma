# CartoPharma

CartoPharma est une application web de cartographie sante/services pour la France.
Le depot contient un backend FastAPI, un frontend Next.js et une base SQLite runtime. A ce stade, les couches et points affiches restent majoritairement mockes, mais l application est lancable et structuree pour evoluer.

## Statut actuel

- version courante : `0.1.1`
- perimetre : France uniquement
- socle fonctionnel disponible : frontend, backend, carte Leaflet, couches activables, settings persistants
- donnees metier reelles : non branchees pour le moment

## Fonctionnalites actuelles

- API FastAPI versionnee sous `/api/v1`
- endpoints de statut et de sante
- catalogue de couches cartographiques
- exposition de points GeoJSON mockes
- persistance SQLite des settings d affichage
- page d accueil `/`
- page carte `/map`
- page parametres `/settings`
- carte Leaflet avec panneau d activation/desactivation des couches

## Structure du depot

- `backend/` : API FastAPI, schemas, routes, acces SQLite
- `frontend/` : application Next.js App Router
- `data/` : base SQLite, logs et fichiers runtime
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
- `GET /api/v1/layers`
- `GET /api/v1/layers/points`

## Donnees et base de donnees

- base par defaut : `data/cartopharma.sqlite`
- logs backend : `data/logs/`
- repertoires runtime : `data/layers/`, `data/tmp/`
- points exposes : actuellement mockes

## Documentation disponible

- `docs/style-frontend-ui.md`
- `docs/metrics_catalog.md`
- `docs/ROADMAP.md`
- `docs/documentation_update_runbook.md`
- `docs/indexation.md`
- `docs/indexation_operational_runbook.md`
- `docs/readme-doc.md`
- `docs/github-push.md`

## Limites actuelles

- pas encore de vraies donnees pharmacies
- pas de calcul de zone de chalandise
- pas de pipeline d ingestion metier complet
- carte et couches encore en base mockee pour la V1 fondation
