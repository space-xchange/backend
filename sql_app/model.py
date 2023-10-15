from sqlalchemy import String, Integer, Column, Float, ForeignKey
from sql_app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(20), unique=False, nullable=False)
    email = Column(String(20), unique=True, nullable=False)
    password = Column(String(20), unique=False, nullable=False)
    address = Column(String(64), unique=True, nullable=False)

class Crypto(Base):
    __tablename__ = "cryptos"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(20), unique=True, nullable=False)
    values = relationship("CryptoValue", back_populates="crypto")

class CryptoValue(Base):
    __tablename__ = "cryptovalues"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    crypto_id = Column(Integer, ForeignKey('cryptos.id'), nullable=False)
    value_eth = Column(Float, nullable=False)
    value_aud = Column(Float, nullable=False)
    time = Column(Integer, nullable=False)
    crypto = relationship("Crypto", back_populates="values")
