from fastapi import APIRouter, HTTPException, status
from app.schemas import LoginRequest, JwtResponse
from app.utils.auth import create_access_token
from app.utils.password import verify_demo_credentials

router = APIRouter(tags=["Auth Controller"])


@router.post("/auth/login", response_model=JwtResponse)
def login(request: LoginRequest):
    if not verify_demo_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    token = create_access_token(data={"sub": request.username})
    return {"token": token}
