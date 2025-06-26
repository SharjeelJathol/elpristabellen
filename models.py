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
    price = Column(Float, nullable=True)
    elomrade_id = Column(Integer, nullable=False)
    postnummer = Column(Integer, nullable=False)

# DB Setup
engine = create_engine("sqlite:///data.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
