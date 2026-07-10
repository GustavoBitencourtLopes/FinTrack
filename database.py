from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.usuario import Base

engine = create_engine("sqlite:///fintrack.db")
Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)