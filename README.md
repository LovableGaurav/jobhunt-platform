# JobHunt Platform

Automated job-hunting for freshers (0–2 years) in ML Engineering, Data Science, and Software Engineering.

## Quick start (local)

### 1. Infrastructure

```bash
# From project root
docker compose up -d
cp .env.example .env
```

### 2. Database migrations

```bash
cd apps/api
pip install -r requirements.txt
# Windows PowerShell:
$env:PYTHONPATH = "..\.."
alembic upgrade head
```

### 3. API

```bash
# From project root
$env:PYTHONPATH = "."
uvicorn apps.api.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

### 4. Celery worker + beat

```bash
pip install -r workers/requirements.txt -r apps/api/requirements.txt
celery -A workers.celery_app worker --loglevel=info
celery -A workers.celery_app beat --loglevel=info
```

### 5. Frontend

```bash
cd apps/web
npm install
npm run dev
```

## Docker (full stack)

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

Run migrations inside the API container after first boot:

```bash
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
```

## Architecture

| Layer | Path |
|-------|------|
| API | `apps/api/` — FastAPI, SQLAlchemy async, pgvector |
| Workers | `workers/` — Celery scrapers + processors |
| Web | `apps/web/` — Next.js 14 dashboard |
| Types | `packages/types/` — shared TS types |

## API routes (`/api/v1`)

- `POST /auth/register`, `POST /auth/login`
- `GET /users/me`
- `GET /jobs`, `GET /jobs/matches`, `GET /jobs/{id}`
- `GET /applications`, `POST /applications`, `GET /applications/{id}`
- `GET /dashboard/stats`

## Environment

See `.env.example` for all variables. Required for full functionality:

- `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`
- `OPENAI_API_KEY` (embeddings + tailoring)

## Tests

```bash
pip install pytest
pytest tests/
```
