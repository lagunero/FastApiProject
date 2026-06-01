import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_PATH = "data/mydatabase.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    from app.models import Base
    
    os.makedirs("data", exist_ok=True)
    
    db_is_new = not os.path.exists(DATABASE_PATH)
    
    Base.metadata.create_all(bind=engine)
    
    if db_is_new:
        db = SessionLocal()
        try:
            with open("init.sql", "r") as f:
                sql_content = f.read()
            
            for statement in sql_content.split(";"):
                statement = statement.strip()
                if statement:
                    db.execute(text(statement))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error loading init.sql: {e}")
        finally:
            db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
