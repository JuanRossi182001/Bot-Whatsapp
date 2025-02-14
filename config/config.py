from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+psycopg2://postgres:holagente56@localhost:5432/ChatBot"

engine = create_engine(DATABASE_URL)
sessionlocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
base = declarative_base()