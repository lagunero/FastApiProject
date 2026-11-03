# Copilot instructions for FastApiProject

## Project overview

This repository is a small FastAPI application with a SQLite database and a JWT-based demo auth flow. The main entry point is `main.py`, which initializes the database and registers three routers:

- `app.routers.auth` – login and JWT issuance
- `app.routers.users` – CRUD for users
- `app.routers.hello` – simple authenticated greeting endpoints

The database is created lazily by `app/database.py::init_db()`, which creates the schema from SQLAlchemy models and then seeds `data/mydatabase.db` from `init.sql` when the file is first created. The important project constraint is that `User.id` is stored as a binary UUID (`LargeBinary`), not as a string; all UUID conversion logic lives in the users router and must stay consistent with `init.sql`.

## Build, run, and test commands

From the repository root:

```powershell
python -m pip install -e .
python main.py
python -m uvicorn main:app --host 0.0.0.0 --port 9080
```

After installation, the project exposes scripts from `pyproject.toml`:

```powershell
fp-start
fp-test-api
fp-init-db
```

Single API check / smoke test (requires the server to already be running):

```powershell
python test_api.py
```

There is no dedicated lint or pytest configuration in this repository; the built-in validation path is the integration script above.

## Architecture and conventions that matter here

- `main.py` bootstraps the app, calls `init_db()` immediately, and includes routers on startup.
- `app/database.py` uses SQLAlchemy `create_engine(..., connect_args={"check_same_thread": False}, poolclass=StaticPool)` and `SessionLocal` for direct session management. The project uses `db = SessionLocal()` with explicit `finally: db.close()` in routes instead of relying on a FastAPI dependency injection pattern throughout.
- `app/models.py` declares the SQLAlchemy model with snake_case column names (`first_name`, `last_name`, `birth_date`, etc.). The `User.id` field is `LargeBinary` storing `uuid.uuid4().bytes`.
- `app/schemas.py` intentionally exposes camelCase API fields via Pydantic aliases and `ConfigDict(populate_by_name=True)`, so JSON payloads use keys like `firstName`, `lastName`, `birthDate`, `createdAt`, and `updatedAt` while the DB model remains snake_case.
- `app/utils/auth.py` creates and verifies JWTs with HS256 (`SECRET_KEY` from `app/config.py`, default value is intentionally a demo secret). Protected endpoints use `Authorization: Bearer <token>` and call `verify_token(token)` to return `{"username": ...}` or `None`.
- `app/utils/password.py` contains the demo credentials (`user`/`admin` with password `password`), and `init.sql` seeds the database with the same usernames and plaintext passwords. If you modify these, keep the seed data and runtime verification logic consistent.
- When changing the schema or seed data, update both `app/models.py` and `init.sql` together; the repo assumes SQLite is initialized from the SQL file once when the database does not exist.
- Before changing API payloads or responses, check `openapi.yaml`; it is the project’s contract reference for expected request/response shapes and examples.

## Working style for this repo

- Prefer the existing router/database pattern over refactoring to a different FastAPI pattern unless the task specifically requires it.
- Keep database field names snake_case and JSON field names camelCase.
- Preserve the binary UUID storage pattern in `app/routers/users.py` and `init.sql` when adding or editing user fields.
- Use the existing `SessionLocal()`/`close()` lifecycle in routers for database access.
- The project is intentionally small and document-light; reading `main.py`, `app/database.py`, `app/models.py`, `app/schemas.py`, and the relevant router is usually enough to understand the behavior.

## Additional repo references

- `openapi.yaml` – canonical API contract and examples
- `postman_collection.json` – manual API smoke-test collection
- `AGENTS.md` – project-specific guidance carried forward for agents and editors
