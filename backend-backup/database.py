from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

sqlalchamy_database_url = "sqlite:///./blog.db"  # Use your actual database URL here
engine = create_engine(sqlalchamy_database_url , connect_args={"check_same_thread": False})
# Base = declarative_base()



from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()