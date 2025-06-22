from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)

class Agreement(Base):
    __tablename__ = 'agreements'
    id = Column(Integer, primary_key=True)           # 'Id' from API
    company = Column(String)
    price = Column(Float)
    contract = Column(Text)
    avtalstid = Column(String)
    monthly_price = Column(Float)
    dynamic_purchase_fee = Column(Float)
    taxes = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)

def get_all_agreements():
    session = Session()
    results = session.query(Agreement).order_by(Agreement.price.asc()).all()
    data = []
    for r in results:
        data.append({
            "id": r.id,
            "company": r.company,
            "price": r.price,
            "contract": r.contract,
            "avtalstid": r.avtalstid,
            "monthly_price": r.monthly_price,
            "dynamic_purchase_fee": r.dynamic_purchase_fee,
            "taxes": r.taxes,
            "fetched_at": r.fetched_at.isoformat()
        })
    session.close()
    return data
