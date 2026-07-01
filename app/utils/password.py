from app.database import SessionLocal
from app.models import User

DEMO_CREDENTIALS = {
    "user": "admin",
    "admin": "admin",
}


def verify_credentials(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_name == username).first()
    finally:
        db.close()
    return user.password == password
