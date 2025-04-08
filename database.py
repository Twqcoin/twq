from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL")  # نأخذ رابط قاعدة البيانات من متغير البيئة

engine = create_engine(DATABASE_URL, connect_args={}, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    points = Column(Integer, default=0)

# إنشاء الجداول في قاعدة البيانات
def init_db():
    Base.metadata.create_all(bind=engine)
