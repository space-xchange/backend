from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import joinedload
import json
from pprint import pprint

from sql_app.model import Base, Crypto, CryptoValue
from sql_app.database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

def populate_db_from_json(json_str, db):
    data = json.loads(json_str)
    
    for id, d in enumerate(data):
        crypto = Crypto(name=d['name'])
        db.add(crypto)
        db.commit()
        for time, val in d['values'].items():
            db.add(CryptoValue(
                crypto_id = crypto.id,
                time = int(time),
                value_aud = val,
                value_eth = data[id]['values'][time] / data[0]['values'][time],
            ))
    db.commit()
    db.close()

with open("data.json", "r") as file:
    json_str = file.read()

session = SessionLocal()
populate_db_from_json(json_str, session)
