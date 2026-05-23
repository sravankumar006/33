# Tech Decision

A full-stack decision support app with a modern Next.js frontend and a FastAPI backend.

## Project structure

- `frontend/` - Next.js 16 App Router UI with TypeScript, Tailwind CSS, shadcn/ui style components, and Lucide icons.
- `backend/` - FastAPI service with SQLAlchemy, PostgreSQL support, Alembic migrations, and a health endpoint.

## Setup

### Backend

1. Create a Python environment and activate it.
2. Install dependencies:

```bash
cd tech-decision/backend
python -m pip install -r requirements.txt
```

3. Create a `.env` file from the example:

```bash
copy .env.example .env
```

4. Update `DATABASE_URL` if needed.

5. Run the backend:

```bash
cd tech-decision/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

5. Seed the database with a sample phone:

```bash
cd tech-decision/backend
python scripts/seed.py
```

6. Verify health:

```bash
curl http://localhost:8000/health
```

### API routes

- `GET /api/phones/search?q=oneplus`
- `GET /api/phones/{slug}`

### Frontend

1. Install dependencies:

```bash
cd tech-decision/frontend
npm install
```

2. Create `.env.local` or copy the example:

```bash
copy .env.example .env.local
```

3. Run the frontend:

```bash
cd tech-decision/frontend
npm run dev
```

4. Open `http://localhost:3000` in your browser.

### Notes

- The frontend uses `NEXT_PUBLIC_API_BASE_URL` to communicate with the backend.
- The backend is configured with CORS to allow the frontend origin.
- The `/health` route returns:

```json
{ "status": "ok" }
```
