# SPEC.md — MyTraining Backend

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & Tech Stack](#2-architecture--tech-stack)
3. [Data Models (Beanie Documents)](#3-data-models-beanie-documents)
4. [API Endpoints & Request/Response Schemas](#4-api-endpoints--requestresponse-schemas)
5. [Authentication & Security](#5-authentication--security)
6. [Error Handling Strategy](#6-error-handling-strategy)
7. [Project Structure](#7-project-structure)

---

## 1. Project Overview

### Description

**MyTraining** is the REST API server powering the MyTraining personal training assistant. It is built with FastAPI and provides secure, authenticated endpoints for managing training sessions, workout units, executed sets, exercises, and catalog data (training types and muscle groups). Data is persisted on MongoDB Atlas via the Beanie ODM.

### Goals

- Expose a clean RESTful API consumed by the Angular frontend.
- Handle JWT-based authentication securely.
- Manage all domain data: sessions, workout units, executed sets, exercises, training types and muscle groups.
- Be easy to run locally via Docker with a single command.
- Connect to MongoDB Atlas for both development and production.

### Future Goals

- Aggregate endpoints to support analytics and progress charts.
- Report generation endpoints (PDF / CSV export).

### Target Environment

- **Development** — Docker container locally, connected to MongoDB Atlas.
- **Production** — deployable to any VPS or cloud provider using the same Docker setup.

---

## 2. Architecture & Tech Stack

### Core Stack

| Concern | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | FastAPI |
| ODM | Beanie (async, Pydantic v2) |
| Database | MongoDB Atlas |
| Authentication | JWT (OAuth2 Password Bearer) |
| Containerization | Docker + Docker Compose |

### Key Libraries

| Library | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `beanie` | MongoDB ODM (built on Motor + Pydantic v2) |
| `pydantic` | Data validation and serialization |
| `pydantic-settings` | Environment variables management |
| `python-jose` | JWT encoding / decoding |
| `passlib` | Password hashing (bcrypt) |
| `python-multipart` | Form data support (required by FastAPI OAuth2) |
| `motor` | Async MongoDB driver (used by Beanie internally) |

### Project Structure

```
mytraining-backend/
├── app/
│   ├── main.py                 # FastAPI app entry point, lifespan, CORS
│   ├── config.py               # Settings via pydantic-settings
│   ├── database.py             # Beanie initialization, Atlas connection
│   ├── auth/
│   │   ├── router.py           # Auth endpoints (login, refresh, me)
│   │   ├── service.py          # JWT logic, password hashing
│   │   └── dependencies.py     # get_current_user dependency
│   ├── routers/
│   │   ├── sessions.py
│   │   ├── workout_units.py
│   │   ├── executed_sets.py
│   │   ├── exercises.py
│   │   ├── training_types.py
│   │   └── muscle_groups.py
│   ├── models/                 # Beanie documents (database layer)
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── exercise.py
│   │   ├── training_type.py
│   │   └── muscle_group.py
│   └── schemas/                # Pydantic request/response schemas (API layer)
│       ├── auth.py
│       ├── session.py
│       ├── workout_unit.py
│       ├── executed_set.py
│       ├── exercise.py
│       ├── training_type.py
│       ├── muscle_group.py
│       └── common.py
├── .env                        # Never committed
├── .env.example                # Committed, shows required variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### Environment Variables (`.env`)

```bash
# MongoDB Atlas
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/mytraining

# JWT
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440      # 1 day

# App
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:4200
```

### Docker Setup

**`Dockerfile`:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**`docker-compose.yml`:**
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
```

### CORS

The Angular frontend runs on `http://localhost:4200` during development. FastAPI allows cross-origin requests from this origin via `CORSMiddleware`, configured through the `ALLOWED_ORIGINS` environment variable.

---

## 3. Data Models (Beanie Documents)

All documents extend Beanie's `Document` class. Embedded documents (`WorkoutUnit`, `ExecutedSet`) extend `BaseModel` since they are nested inside `Session` and not stored in separate collections.

> **Eager fetching policy:** all `Link[]` references are always eagerly fetched using Beanie's `fetch_links=True` parameter. Every read returns fully populated documents.

---

### TrainingType

Collection: `training-types`

```python
class TrainingType(Document):
    name: str
    description: str

    class Settings:
        name = "training-types"
```

---

### MuscleGroup

Collection: `muscle-groups`

```python
class MuscleGroup(Document):
    name: str
    description: str | None = None

    class Settings:
        name = "muscle-groups"
```

---

### Exercise

Collection: `exercises`

```python
class Exercise(Document):
    name: str
    training_type: Link[TrainingType]
    muscle_group: Link[MuscleGroup]
    execution_description: str
    load_description: str
    notes: str | None = None

    class Settings:
        name = "exercises"
```

---

### ExecutedSet (embedded)

Not a separate collection — embedded inside `WorkoutUnit`.

```python
class ExecutedSet(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    exercise: Link[Exercise]
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None
```

---

### WorkoutUnit (embedded)

Not a separate collection — embedded inside `Session`.

```python
class WorkoutUnit(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    training_type: Link[TrainingType]
    executed_sets: list[ExecutedSet] = []
    total_load_description: str
    notes: str | None = None
```

---

### Session

Collection: `sessions`

```python
class Session(Document):
    user_id: str
    name: str
    date: datetime
    workout_units: list[WorkoutUnit] = []
    total_load_description: str
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "sessions"
```

---

### User

Collection: `users`

```python
class User(Document):
    email: str
    display_name: str
    description: str | None = None
    password_hash: str

    class Settings:
        name = "users"
```

---

### MongoDB Document Structure Summary

| Collection | Type | Notes |
|---|---|---|
| `training-types` | `Document` | Standalone collection |
| `muscle-groups` | `Document` | Standalone collection |
| `exercises` | `Document` | References `TrainingType` and `MuscleGroup` |
| `sessions` | `Document` | Contains embedded `WorkoutUnit` list |
| `users` | `Document` | Standalone collection |
| `WorkoutUnit` | `BaseModel` | Embedded in `Session` |
| `ExecutedSet` | `BaseModel` | Embedded in `WorkoutUnit` |

---

### Embedding vs Referencing Decision

| Relationship | Strategy | Reason |
|---|---|---|
| Session → WorkoutUnit | **Embedded** | Units only exist within a session, always loaded together |
| WorkoutUnit → ExecutedSet | **Embedded** | Sets only exist within a unit, always loaded together |
| WorkoutUnit → TrainingType | **Referenced** | Catalog data, shared across documents |
| ExecutedSet → Exercise | **Referenced** | Catalog data, shared across documents |
| Exercise → TrainingType | **Referenced** | Catalog data, shared across documents |
| Exercise → MuscleGroup | **Referenced** | Catalog data, shared across documents |

---

## 4. API Endpoints & Request/Response Schemas

Base URL: `/api/v1`

> All endpoints except `POST /auth/login` require a valid JWT token in the `Authorization: Bearer <token>` header.

> **Computed fields** (`totalLoad` at set, unit, and session level) are calculated on the frontend. The API never returns nor stores them.

> **Mutation response policy:** all `POST`, `PUT`, `PATCH` and `DELETE` operations on workout units and executed sets return the full `SessionResponse` (with all nested data eagerly fetched), allowing the frontend `sessionsStore` to replace the entire selected session in a single operation.

---

### 4.1 Auth

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Login, returns JWT access token |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current authenticated user |

#### Schemas

```python
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int             # seconds, e.g. 86400 for 1 day

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    description: str | None = None
```

---

### 4.2 Training Types

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/training-types` | List all training types |
| POST | `/training-types` | Create a training type |
| PUT | `/training-types/{id}` | Update a training type |
| DELETE | `/training-types/{id}` | Delete a training type |

#### Schemas

```python
class TrainingTypeCreate(BaseModel):
    name: str
    description: str

class TrainingTypeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class TrainingTypeResponse(BaseModel):
    id: str
    name: str
    description: str
```

> **Delete policy:** returns `409 Conflict` if the training type is referenced by any exercise or workout unit.

---

### 4.3 Muscle Groups

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/muscle-groups` | List all muscle groups |
| POST | `/muscle-groups` | Create a muscle group |
| PUT | `/muscle-groups/{id}` | Update a muscle group |
| DELETE | `/muscle-groups/{id}` | Delete a muscle group |

#### Schemas

```python
class MuscleGroupCreate(BaseModel):
    name: str
    description: str | None = None

class MuscleGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class MuscleGroupResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
```

> **Delete policy:** returns `409 Conflict` if the muscle group is referenced by any exercise.

---

### 4.4 Exercises

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/exercises` | List all exercises (supports `?trainingTypeId=`, `?muscleGroupId=`) |
| GET | `/exercises/{id}` | Get exercise detail |
| POST | `/exercises` | Create an exercise |
| PUT | `/exercises/{id}` | Update an exercise |
| DELETE | `/exercises/{id}` | Delete an exercise |

#### Schemas

```python
class ExerciseCreate(BaseModel):
    name: str
    training_type_id: str
    muscle_group_id: str
    execution_description: str
    load_description: str
    notes: str | None = None

class ExerciseUpdate(BaseModel):
    name: str | None = None
    training_type_id: str | None = None
    muscle_group_id: str | None = None
    execution_description: str | None = None
    load_description: str | None = None
    notes: str | None = None

class ExerciseResponse(BaseModel):
    id: str
    name: str
    training_type: TrainingTypeResponse     # fully populated
    muscle_group: MuscleGroupResponse       # fully populated
    execution_description: str
    load_description: str
    notes: str | None = None
```

> **Delete policy:** returns `409 Conflict` if the exercise is referenced by any executed set.

---

### 4.5 Sessions

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/sessions` | List sessions (supports `?date=`, `?from=`, `?to=`, `?limit=`, `?skip=`) |
| GET | `/sessions/{id}` | Get full session detail |
| POST | `/sessions` | Create a new session |
| PUT | `/sessions/{id}` | Update a session |
| DELETE | `/sessions/{id}` | Delete a session |

#### Schemas

```python
class SessionCreate(BaseModel):
    name: str
    date: datetime
    total_load_description: str
    notes: str | None = None

class SessionUpdate(BaseModel):
    name: str | None = None
    date: datetime | None = None
    total_load_description: str | None = None
    notes: str | None = None

class SessionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    date: datetime
    workout_units: list[WorkoutUnitResponse]    # fully populated
    total_load_description: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

class SessionListItemResponse(BaseModel):
    id: str
    name: str
    date: datetime
    workout_units: list[WorkoutUnitSummaryResponse]  # name + training type only
    total_load_description: str
```

> `SessionListItemResponse` is a lightweight response for the session list page. `SessionResponse` is the full version returned by `GET /sessions/{id}` and all mutation endpoints.

---

### 4.6 Workout Units

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/sessions/{sessionId}/units` | Add a workout unit |
| PUT | `/sessions/{sessionId}/units/{unitId}` | Update a workout unit |
| DELETE | `/sessions/{sessionId}/units/{unitId}` | Remove a workout unit |
| PATCH | `/sessions/{sessionId}/units/reorder` | Reorder workout units |

#### Schemas

```python
class WorkoutUnitCreate(BaseModel):
    training_type_id: str
    total_load_description: str
    notes: str | None = None

class WorkoutUnitUpdate(BaseModel):
    training_type_id: str | None = None
    total_load_description: str | None = None
    notes: str | None = None

class WorkoutUnitResponse(BaseModel):
    id: str
    training_type: TrainingTypeResponse     # fully populated
    executed_sets: list[ExecutedSetResponse]
    total_load_description: str
    notes: str | None = None

class WorkoutUnitSummaryResponse(BaseModel):
    id: str
    training_type: TrainingTypeResponse     # for session list row

class ReorderRequest(BaseModel):
    ordered_ids: list[str]                  # full list of ids in new order
```

---

### 4.7 Executed Sets

#### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/sessions/{sessionId}/units/{unitId}/sets` | Add an executed set |
| PUT | `/sessions/{sessionId}/units/{unitId}/sets/{setId}` | Update an executed set |
| DELETE | `/sessions/{sessionId}/units/{unitId}/sets/{setId}` | Remove an executed set |
| PATCH | `/sessions/{sessionId}/units/{unitId}/sets/reorder` | Reorder executed sets |

#### Schemas

```python
class ExecutedSetCreate(BaseModel):
    exercise_id: str
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None

class ExecutedSetUpdate(BaseModel):
    exercise_id: str | None = None
    load: float | None = None
    load_description: str | None = None
    repetitions: int | None = None
    notes: str | None = None

class ExecutedSetResponse(BaseModel):
    id: str
    exercise: ExerciseResponse              # fully populated
    load: float
    load_description: str
    repetitions: int
    notes: str | None = None
```

---

## 5. Authentication & Security

### Overview

MyTraining uses **JWT (JSON Web Token)** authentication via FastAPI's OAuth2 Password Bearer scheme. The user is created directly in the database — there is no public registration endpoint.

---

### Authentication Flow

```
1. User submits email + password → POST /auth/login
2. FastAPI verifies credentials against the hashed password in MongoDB
3. If valid → returns a signed JWT access token
4. Frontend stores the token in localStorage
5. All subsequent requests include the token in the Authorization header:
   Authorization: Bearer <token>
6. FastAPI validates the token on every protected endpoint via
   the get_current_user dependency
7. On any 401 response → Angular HttpInterceptor calls POST /auth/refresh
8. If refresh succeeds → original request is retried with the new token
9. If refresh fails (token expired) → user is redirected to /auth/login
```

---

### JWT Configuration

| Parameter | Value |
|---|---|
| Algorithm | `HS256` |
| Expiry | 1 day (1440 minutes) |
| Secret | `JWT_SECRET` environment variable |
| Token type | Bearer |
| Storage (frontend) | `localStorage` |

---

### Token Refresh Strategy

**Reactive refresh** — implemented in the Angular `HttpInterceptor`:

```
Any API request → 401 Unauthorized
→ POST /auth/refresh (with current token)
  → Success → retry original request with new token
  → Failure (token expired) → redirect to /auth/login
```

The `/auth/refresh` endpoint only accepts **still-valid tokens**. If the token is already expired, the user must log in again.

---

### Password Hashing

Passwords are **never stored in plain text**. The `passlib` library with `bcrypt` is used for hashing and verification:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

### `get_current_user` Dependency

Every protected endpoint injects this dependency to validate the JWT and return the authenticated user:

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jose.jwt.decode(
            token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await User.get(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

---

### `user_id` Filtering on Sessions

Session endpoints enforce data isolation at the **router level**. Every query explicitly filters by the `user_id` extracted from the JWT token:

```python
# Example — GET /sessions
@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user)
):
    sessions = await Session.find(
        Session.user_id == str(current_user.id)
    ).to_list()
    return sessions
```

---

### CORS Policy

| Setting | Value |
|---|---|
| Allowed origins | `ALLOWED_ORIGINS` env variable |
| Allowed methods | `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS` |
| Allowed headers | `Authorization`, `Content-Type` |
| Allow credentials | `True` |

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

---

### Security Rules Summary

- All endpoints except `POST /auth/login` require a valid JWT token.
- Sessions are always filtered by `user_id` at the router level.
- `password_hash` is never included in any response schema.
- `JWT_SECRET` is never committed to the repository — it lives exclusively in `.env`.

---

## 6. Error Handling Strategy

### Overview

All errors are returned as JSON responses with a consistent structure, using standard HTTP status codes. FastAPI handles most of this automatically via `HTTPException` and Pydantic validation errors.

---

### Standard Error Response Format

```json
{
  "detail": "A clear, human-readable error message"
}
```

For validation errors (Pydantic), FastAPI automatically returns a more detailed structure:

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

### HTTP Status Codes

| Code | Meaning | When used |
|---|---|---|
| `200 OK` | Success | Successful GET, PUT, PATCH |
| `201 Created` | Resource created | Successful POST |
| `204 No Content` | Resource deleted | Successful DELETE (no body returned) |
| `400 Bad Request` | Invalid input | Malformed request body |
| `401 Unauthorized` | Authentication failed | Missing or invalid JWT |
| `403 Forbidden` | Authorization failed | Valid JWT but wrong user |
| `404 Not Found` | Resource not found | Document not in MongoDB |
| `409 Conflict` | Delete blocked | Referenced resource cannot be deleted |
| `422 Unprocessable Entity` | Validation error | Pydantic validation failure |
| `500 Internal Server Error` | Unexpected error | Unhandled exceptions |

> **Note:** DELETE endpoints for workout units and executed sets also return `204 No Content`. The frontend `sessionsStore` reloads the full session after every mutation.

---

### Reference Conflict Handling (409)

Deletion of referenced resources is blocked with a `409 Conflict`:

```python
# Example — DELETE /training-types/{id}
async def delete_training_type(id: str):
    referenced_by_exercises = await Exercise.find(
        Exercise.training_type.id == PydanticObjectId(id)
    ).count()

    referenced_by_units = await Session.find(
        Session.workout_units.training_type.id == PydanticObjectId(id)
    ).count()

    total = referenced_by_exercises + referenced_by_units
    if total > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Training type is referenced by {total} document(s) and cannot be deleted."
        )
```

The same pattern applies to `MuscleGroup` and `Exercise` deletions.

---

### Global Exception Handler

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."}
    )
```

---

### Not Found Helper

```python
def raise_not_found(resource: str = "Resource"):
    raise HTTPException(
        status_code=404,
        detail=f"{resource} not found."
    )

# Usage
session = await Session.get(id)
if session is None:
    raise_not_found("Session")
```

---

### Logging Strategy

Python's built-in `logging` module is used throughout the application.

**Configuration (`main.py`):**

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("mytraining")
```

**Usage across modules:**

```python
import logging
logger = logging.getLogger("mytraining")

logger.info(f"Session {session_id} created by user {user_id}")
logger.warning(f"Delete blocked: TrainingType {id} is referenced by {total} document(s)")
logger.error(f"Unhandled exception: {exc}", exc_info=True)
```

**Log levels:**

| Level | When |
|---|---|
| `INFO` | Successful operations (create, update, delete) |
| `WARNING` | Blocked operations (409 conflicts, 404 not found) |
| `ERROR` | Unhandled exceptions (500 errors) |

> During development logs are printed to the console via `uvicorn`. In production the same logs are captured by the Docker container's stdout.

---

### Validation Errors

Pydantic v2 automatically validates all request bodies. If validation fails, FastAPI returns `422 Unprocessable Entity` with field-level details. No additional configuration needed.

---

## 7. Project Structure

### Full Project Layout

```
mytraining-backend/
├── app/
│   ├── main.py                 # FastAPI app entry point, lifespan,
│   │                           # CORS, logging, exception handler
│   ├── config.py               # Settings via pydantic-settings
│   ├── database.py             # Beanie initialization, Atlas connection
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py           # POST /auth/login, /auth/refresh, GET /auth/me
│   │   ├── service.py          # JWT encoding/decoding, password hashing
│   │   └── dependencies.py     # get_current_user dependency
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── sessions.py         # Session CRUD endpoints
│   │   ├── workout_units.py    # Workout unit endpoints (nested under sessions)
│   │   ├── executed_sets.py    # Executed set endpoints (nested under units)
│   │   ├── exercises.py        # Exercise CRUD endpoints
│   │   ├── training_types.py   # Training type CRUD endpoints
│   │   └── muscle_groups.py    # Muscle group CRUD endpoints
│   │
│   ├── models/                 # Beanie documents (database layer)
│   │   ├── __init__.py
│   │   ├── user.py             # User document → collection: users
│   │   ├── session.py          # Session document + embedded WorkoutUnit,
│   │   │                       # ExecutedSet → collection: sessions
│   │   ├── exercise.py         # Exercise document → collection: exercises
│   │   ├── training_type.py    # TrainingType document → collection: training-types
│   │   └── muscle_group.py     # MuscleGroup document → collection: muscle-groups
│   │
│   └── schemas/                # Pydantic request/response schemas (API layer)
│       ├── __init__.py
│       ├── auth.py             # LoginRequest, TokenResponse, UserResponse
│       ├── session.py          # SessionCreate, SessionUpdate,
│       │                       # SessionResponse, SessionListItemResponse
│       ├── workout_unit.py     # WorkoutUnitCreate, WorkoutUnitUpdate,
│       │                       # WorkoutUnitResponse, WorkoutUnitSummaryResponse
│       ├── executed_set.py     # ExecutedSetCreate, ExecutedSetUpdate,
│       │                       # ExecutedSetResponse
│       ├── exercise.py         # ExerciseCreate, ExerciseUpdate, ExerciseResponse
│       ├── training_type.py    # TrainingTypeCreate, TrainingTypeUpdate,
│       │                       # TrainingTypeResponse
│       ├── muscle_group.py     # MuscleGroupCreate, MuscleGroupUpdate,
│       │                       # MuscleGroupResponse
│       └── common.py           # Shared schemas (ReorderRequest)
│
├── .env                        # Never committed — contains secrets
├── .env.example                # Committed — documents required variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

### Key File Responsibilities

#### `main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_beanie(
        database=db,
        document_models=[
            User, Session, Exercise, TrainingType, MuscleGroup
        ]
    )
    yield

app = FastAPI(lifespan=lifespan)
```

#### `config.py`

```python
class Settings(BaseSettings):
    mongo_uri: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    allowed_origins: list[str] = ["http://localhost:4200"]
    app_env: str = "development"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

#### `database.py`

```python
client = AsyncIOMotorClient(settings.mongo_uri)
db = client.mytraining
```

---

### `.env.example`

```bash
# MongoDB Atlas
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/mytraining

# JWT
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# App
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:4200
```

---

### `.gitignore` (relevant entries)

```
.env
__pycache__/
*.pyc
.venv/
*.egg-info/
.pytest_cache/
```

---

### `requirements.txt`

```
fastapi
uvicorn[standard]
beanie
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
motor
```

---

### `README.md` Structure

```markdown
# MyTraining Backend

## Prerequisites
- Docker Desktop installed
- MongoDB Atlas account and cluster
- Git

## Getting Started

### 1. Clone the repository
git clone https://github.com/your-username/mytraining-backend.git
cd mytraining-backend

### 2. Configure environment variables
cp .env.example .env
# Edit .env with your Atlas URI, JWT secret, etc.

### 3. Run with Docker
docker compose up
# The API will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs

### 4. Stop the app
docker compose down

## Environment Variables
| Variable             | Description                        | Example                          |
|---|---|---|
| MONGO_URI            | MongoDB Atlas connection string    | mongodb+srv://...                |
| JWT_SECRET           | Secret key for JWT signing         | a_long_random_string             |
| JWT_ALGORITHM        | JWT algorithm                      | HS256                            |
| JWT_EXPIRE_MINUTES   | Token expiry in minutes            | 1440                             |
| APP_ENV              | Application environment            | development                      |
| ALLOWED_ORIGINS      | Allowed CORS origins               | http://localhost:4200            |

## API Documentation
FastAPI automatically generates interactive API docs:
- Swagger UI → http://localhost:8000/docs
- ReDoc     → http://localhost:8000/redoc

## Project Structure
See SPEC.md for full architecture and design decisions.
```

---

*Last updated: April 2026*
