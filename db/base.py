from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

Engine = create_engine("sqlite:///db/jobboard.db")
localsession = sessionmaker(bind=Engine, autoflush=True)

class Base(DeclarativeBase):
    pass