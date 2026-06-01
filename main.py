from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import traceback

from app.database import init_db
from app.routers import auth, users, hello

app = FastAPI(
    title="ProyectoDemoSpring API",
    description="API REST de demostración con FastAPI y SQLite",
    version="1.0.0",
)

init_db()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(hello.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    error_response = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": exc.status_code,
        "error": "Error",
        "message": exc.detail,
        "path": str(request.url.path)
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI CRUD Application"}


def run(host: str = "0.0.0.0", port: int = 9080):
    """Start the uvicorn server (exposed for project scripts).

    Use as entry point: `main:run` from pyproject scripts.
    """
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run()
