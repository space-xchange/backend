from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from typing import Generator, Annotated
from fastapi import Depends

# DATABASE_URL = "mariadb+pymysql://s103808977:300903@feenix-mariadb.swin.edu.au/s103808977_db"

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_session() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

DatabaseSession = Annotated[Session, Depends(get_db_session)]
