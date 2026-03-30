# CartoPharma

Application web France-only inspiree d une application de reference, avec une architecture frontend/backend separee, une carte Leaflet et une base technique extensible.

## Structure

- `backend/` : API FastAPI (routes versionnées, schémas Pydantic, données mockées)
- `frontend/` : Next.js App Router + Tailwind v4 + React Query + Leaflet
- `data/` : base SQLite et fichiers runtime du projet
- `docs/` : documentation adaptee au projet

## Démarrage rapide

### Backend

```bash
start_backend.bat
```

### Frontend

```bash
start_frontend.bat
```

### Lancement complet Windows

```bash
run_win.bat
```

### Smoke check scripts

```bash
run_win.bat --smoke
```

### Docker

```bash
docker build -t cartopharma .
docker run --rm -p 3000:3000 -v ${PWD}/data:/data cartopharma
```

Frontend: http://localhost:3000
Backend API docs: http://localhost:8000/docs

## Routes de base

- `/` : accueil
- `/settings` : paramètres
- `/map` : carte interactive + couches mockées

## Non inclus à ce stade

- Calcul de zone de chalandise (prévu pour une version ultérieure)
- Intégration des sources métiers réelles

## Runtime data

- Base par defaut : `data/cartopharma.sqlite`
- Logs backend : `data/logs/`
Application pour cartographier les pharmacies ainsi que les points d'intérêts autour d'elles
