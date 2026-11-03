from fastapi import APIRouter
from app.schemas import HelloMessage

router = APIRouter(tags=["Hello"])


@router.get("/api/v1/hello", response_model=HelloMessage, operation_id="hello")
def hello():
    return {"message": "Hello, world!"}


@router.get(
    "/api/v1/hello/{name}",
    response_model=HelloMessage,
    operation_id="helloWithName",
)
def hello_with_name(name: str):
    return {"message": f"Hello, {name}!"}
