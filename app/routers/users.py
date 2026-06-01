import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.schemas import UserDto
from app.utils.auth import verify_token
from typing import Optional

router = APIRouter(tags=["User Controller"])


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


def uuid_to_string(uuid_bytes):
    if isinstance(uuid_bytes, bytes):
        return str(uuid.UUID(bytes=uuid_bytes))
    return str(uuid_bytes)


def user_to_dto(user: User) -> UserDto:
    return UserDto(
        id=uuid_to_string(user.id),
        firstName=user.first_name,
        lastName=user.last_name,
        email=user.email,
        birthDate=user.birth_date.isoformat() if user.birth_date else None,
        createdAt=user.created_at.isoformat() if user.created_at else None,
        updatedAt=user.updated_at.isoformat() if user.updated_at else None,
    )


def user_dto_to_dict(dto: UserDto) -> dict:
    return dto.model_dump(exclude_none=False)


@router.post("/api/v1/users", response_model=dict)
def create_user(user_data: UserDto, current_user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        new_user = User(
            id=uuid.uuid4().bytes,
            first_name=user_data.firstName,
            last_name=user_data.lastName,
            email=user_data.email,
            birth_date=datetime.fromisoformat(user_data.birthDate).date() if user_data.birthDate else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return user_dto_to_dict(user_to_dto(new_user))
    finally:
        db.close()


@router.get("/api/v1/users", response_model=list[dict])
def find_all_users(current_user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [user_dto_to_dict(user_to_dto(u)) for u in users]
    finally:
        db.close()


@router.get("/api/v1/users/{user_id}", response_model=dict)
def find_user_by_id(user_id: str, current_user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user_uuid = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid.bytes).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        return user_dto_to_dict(user_to_dto(user))
    finally:
        db.close()


@router.put("/api/v1/users/{user_id}", response_model=dict)
def update_user(user_id: str, user_data: UserDto, current_user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user_uuid = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid.bytes).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        user.first_name = user_data.firstName
        user.last_name = user_data.lastName
        user.email = user_data.email
        user.birth_date = datetime.fromisoformat(user_data.birthDate).date() if user_data.birthDate else None
        user.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(user)
        return user_dto_to_dict(user_to_dto(user))
    finally:
        db.close()


@router.delete("/api/v1/users/{user_id}")
def delete_user(user_id: str, current_user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        user_uuid = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == user_uuid.bytes).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    finally:
        db.close()


@router.delete("/api/v1/users")
def delete_all_users(current_user = Depends(get_current_user)):
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
        return {"message": "All users deleted successfully"}
    finally:
        db.close()
