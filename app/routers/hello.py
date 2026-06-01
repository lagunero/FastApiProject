from fastapi import APIRouter, HTTPException, status, Header, Depends
from app.schemas import HelloMessage
from app.utils.auth import verify_token
from typing import Optional

router = APIRouter(tags=["Hello Controller"])


def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    user_info = verify_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_info


@router.get("/api/v1/hello", response_model=HelloMessage)
def hello(current_user = Depends(get_current_user)):
    return {"message": "Hello, World!"}


@router.get("/api/v1/hello/{name}", response_model=HelloMessage)
def hello_with_name(name: str, current_user = Depends(get_current_user)):
    return {"message": f"Hello, {name}!"}
