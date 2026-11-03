from fastapi import APIRouter, status
from fastapi.responses import PlainTextResponse
from app.schemas import LoginRequest, JwtResponse
from app.utils.auth import create_access_token
from app.utils.password import verify_credentials
import logging

router = APIRouter(tags=["Auth"])


@router.post(
    "/auth/login",
    response_model=JwtResponse,
    operation_id="login",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Usuario o contraseña incorrectos.",
            "content": {
                "text/plain": {
                    "schema": {"type": "string"},
                    "example": "Incorrect username or password",
                }
            },
        }
    },
)
def login(request: LoginRequest):
    if not verify_credentials(request.username, request.password):
        return PlainTextResponse(
            "Incorrect username or password",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    logging.log(logging.INFO, f"User '{request.username}' logged in successfully")
    token = create_access_token(data={"sub": request.username})
    return {"token": token}
