from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Agreement(Base):
    __tablename__ = "agreements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    company = Column(String, nullable=False)
    # contract_type = Column(String, nullable=False)
    price_monthly = Column(Float, nullable=True)
    price_hourly = Column(Float, nullable=True)
    price_fast = Column(Float, nullable=True)
    # price = Column(Float, nullable=True)
    price_fast_3m = Column(Float, nullable=True)
    price_fast_6m = Column(Float, nullable=True)
    price_fast_1y = Column(Float, nullable=True)
    price_fast_2y = Column(Float, nullable=True)
    price_fast_3y = Column(Float, nullable=True)
    price_fast_4y = Column(Float, nullable=True)
    price_fast_5y = Column(Float, nullable=True)
    price_fast_10y = Column(Float, nullable=True)
    elomrade_id = Column(Integer, nullable=False)
    postnummer = Column(Integer, nullable=False)

# DB Setup
engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
