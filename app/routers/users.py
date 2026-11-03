import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.database import SessionLocal
from app.models import User
from app.schemas import UserDto
from app.utils.auth import verify_token
from typing import Optional
import logging as log

router = APIRouter(tags=["Users"])
bearer_scheme = HTTPBearer(auto_error=False, scheme_name="bearerAuth")
USER_AUTH_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: {
        "description": "No se proporcionó un token válido o el token ha expirado.",
    }
}
ADMIN_RESPONSES = {
    **USER_AUTH_RESPONSES,
    status.HTTP_403_FORBIDDEN: {
        "description": "El usuario autenticado no tiene el rol ADMIN necesario.",
    },
}


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user_info = verify_token(credentials.credentials)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_info


def require_admin(current_user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == current_user["username"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        if user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator role required",
            )
        return current_user
    finally:
        db.close()


def uuid_to_string(uuid_bytes):
    if isinstance(uuid_bytes, bytes):
        return str(uuid.UUID(bytes=uuid_bytes))
    return str(uuid_bytes)


def user_to_dto(user: User) -> UserDto:
    return UserDto(
        id=uuid_to_string(user.id),
        userName=user.user_name,
        password=user.password,
        role=user.role,
        firstName=user.first_name,
        lastName=user.last_name,
        email=user.email,
        birthDate=user.birth_date,
        createdAt=user.created_at,
        updatedAt=user.updated_at,
    )


def user_dto_to_dict(dto: UserDto) -> dict:
    return dto.model_dump(mode="json", exclude_none=False)


@router.post(
    "/api/v1/users",
    response_model=UserDto,
    response_model_by_alias=False,
    operation_id="createUser",
    responses=ADMIN_RESPONSES,
)
def create_user(user_data: UserDto, current_user=Depends(require_admin)):
    db = SessionLocal()
    try:
        new_user = User(
            id=uuid.uuid4().bytes,
            user_name=user_data.userName,
            password=user_data.password,
            role=user_data.role,
            first_name=user_data.firstName,
            last_name=user_data.lastName,
            email=user_data.email,
            birth_date=user_data.birthDate,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return user_dto_to_dict(user_to_dto(new_user))
    finally:
        db.close()


@router.get(
    "/api/v1/users",
    response_model=list[UserDto],
    response_model_by_alias=False,
    operation_id="findAllUsers",
    responses=USER_AUTH_RESPONSES,
)
def find_all_users(current_user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return [user_dto_to_dict(user_to_dto(u)) for u in users]
    finally:
        db.close()


@router.get(
    "/api/v1/users/{user_id}",
    response_model=Optional[UserDto],
    response_model_by_alias=False,
    operation_id="findUserById",
    responses=USER_AUTH_RESPONSES,
)
def find_user_by_id(user_id: uuid.UUID, current_user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id.bytes).first()
        if user:
            log.log(log.INFO, f"User with id {user_id} found")
            return user_to_dto(user)
        return None
    finally:
        db.close()


@router.put(
    "/api/v1/users/{user_id}",
    response_model=Optional[UserDto],
    response_model_by_alias=False,
    operation_id="updateUser",
    responses=ADMIN_RESPONSES,
)
def update_user(
    user_id: uuid.UUID,
    user_data: UserDto,
    current_user=Depends(require_admin),
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id.bytes).first()
        if not user:
            return None

        updates = {
            "user_name": user_data.userName,
            "password": user_data.password,
            "role": user_data.role,
            "first_name": user_data.firstName,
            "last_name": user_data.lastName,
            "email": user_data.email,
            "birth_date": user_data.birthDate,
        }
        for field, value in updates.items():
            if value is not None:
                setattr(user, field, value)
        user.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(user)
        return user_to_dto(user)
    finally:
        db.close()


@router.delete(
    "/api/v1/users/{user_id}",
    response_class=Response,
    operation_id="deleteUser",
    responses=ADMIN_RESPONSES,
)
def delete_user(user_id: uuid.UUID, current_user=Depends(require_admin)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id.bytes).first()
        if user:
            db.delete(user)
            db.commit()
        return Response(status_code=status.HTTP_200_OK)
    finally:
        db.close()


@router.delete(
    "/api/v1/users",
    response_class=Response,
    operation_id="deleteAllUsers",
    responses=ADMIN_RESPONSES,
)
def delete_all_users(current_user=Depends(require_admin)):
    db = SessionLocal()
    try:
        db.query(User).delete()
        db.commit()
        return Response(status_code=status.HTTP_200_OK)
    finally:
        db.close()
