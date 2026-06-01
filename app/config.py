import os
from datetime import timedelta

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

DATABASE_URL = "sqlite:///./data/mydatabase.db"
