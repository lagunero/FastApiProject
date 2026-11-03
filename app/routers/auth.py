from fastapi import APIRouter, HTTPException, status
from app.schemas import LoginRequest, JwtResponse
from app.utils.auth import create_access_token
from app.utils.password import verify_credentials
import logging

router = APIRouter(tags=["Auth Controller"])



@router.post("/auth/login", response_model=JwtResponse)
def login(request: LoginRequest):
    if not verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )

    logging.log(logging.INFO, f"User '{request.username}' logged in successfully")
    token = create_access_token(data={"sub": request.username})
    return {"token": token}
