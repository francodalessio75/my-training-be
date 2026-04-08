# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
We are building the app described in @SPEC.md. Read that file for general architectural tasks or to double-check the exact database structure,
tech stack or application architecture.
Keep your replies extremely concise and focus on conveying the key information. No unnecessary fluff, no long code snippet.

## Commands

```bash
# Run the development server
source venv/Scripts/activate
uvicorn app.main:app --reload

# Run with Docker
docker compose up
```

API available at `http://localhost:8000` — Swagger UI at `http://localhost:8000/docs`.

No test suite exists yet.

## Architecture

**SPEC.md is the authoritative design document.** All architectural decisions are defined there. The current `main.py` is a minimal skeleton — the full implementation follows the structure below.

### Tech Stack

- FastAPI + Uvicorn, Python 3.12+
- Beanie ODM (async, Pydantic v2) on top of Motor → MongoDB Atlas
- JWT authentication (HS256, 1-day expiry) via OAuth2 Password Bearer
- Docker + Docker Compose for containerization

### Target Project Structure

```
app/
├── main.py           # FastAPI app, lifespan (Beanie init), CORS, logging, global exception handler
├── config.py         # pydantic-settings: MONGO_URI, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, ALLOWED_ORIGINS
├── database.py       # AsyncIOMotorClient + Beanie init_beanie()
├── auth/
│   ├── router.py     # POST /auth/login, POST /auth/refresh, GET /auth/me
│   ├── service.py    # JWT encode/decode, bcrypt hash/verify
│   └── dependencies.py  # get_current_user dependency (injected into all protected endpoints)
├── routers/          # One file per resource
├── models/           # Beanie Documents (database layer)
└── schemas/          # Pydantic request/response schemas (API layer)
```

### Data Model Key Points

- `WorkoutUnit` and `ExecutedSet` are **embedded** in `Session` (not separate collections)
- `Exercise`, `TrainingType`, `MuscleGroup` are **referenced** via Beanie `Link[]`
- All reads use `fetch_links=True` (eager fetching — always return fully populated documents)
- MongoDB collections: `training-types`, `muscle-groups`, `exercises`, `sessions`, `users`

### API

- Base path: `/api/v1`
- All endpoints except `POST /auth/login` require `Authorization: Bearer <token>`
- Sessions are always filtered by `user_id` extracted from the JWT (data isolation at router level)
- Mutation endpoints on workout units and executed sets return the full `SessionResponse`

### Error Handling

- `409 Conflict` when deleting a resource that is referenced by other documents
- `404` via `raise_not_found(resource)` helper
- Global exception handler logs and returns `500` for unhandled errors
- DELETE returns `204 No Content`

### Environment Variables

```
MONGO_URI          # MongoDB Atlas connection string
JWT_SECRET         # Secret key for JWT signing
JWT_ALGORITHM      # HS256
JWT_EXPIRE_MINUTES # 1440 (1 day)
APP_ENV            # development | production
ALLOWED_ORIGINS    # http://localhost:4200
```
