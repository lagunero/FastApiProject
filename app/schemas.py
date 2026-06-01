from pydantic import BaseModel, Field, ConfigDict
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
    firstName: str = Field(alias="first_name")
    lastName: str = Field(alias="last_name")
    email: str
    birthDate: Optional[str] = Field(default=None, alias="birth_date")
    createdAt: Optional[str] = Field(default=None, alias="created_at")
    updatedAt: Optional[str] = Field(default=None, alias="updated_at")


class HelloMessage(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    timestamp: str
    status: int
    error: str
    message: str
    path: str
