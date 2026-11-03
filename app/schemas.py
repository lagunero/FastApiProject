from pydantic import AliasChoices, BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import Optional


class LoginRequest(BaseModel):
    username: str
    password: str


class JwtResponse(BaseModel):
    token: str


class UserDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    userName: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("userName", "user_name"),
    )
    password: Optional[str] = None
    role: Optional[str] = None
    firstName: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("firstName", "first_name"),
    )
    lastName: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("lastName", "last_name"),
    )
    email: Optional[str] = None
    birthDate: Optional[date] = Field(
        default=None,
        validation_alias=AliasChoices("birthDate", "birth_date"),
    )
    createdAt: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("createdAt", "created_at"),
    )
    updatedAt: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("updatedAt", "updated_at"),
    )


class HelloMessage(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    timestamp: str
    status: int
    error: str
    message: str
    path: str
