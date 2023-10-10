from sqlalchemy import String, Integer, Text, Boolean, Column
from sql_app.database import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(20), unique=False, nullable=False)
    email = Column(String(20), unique=True, nullable=False)
    password = Column(String(20), unique=False, nullable=False)