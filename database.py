from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime

# Базовый класс для моделей
Base = declarative_base()

# Модель Debtor
class Debtor(Base):
    __tablename__ = 'debtors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

# Подключение к базе данных
DATABASE_URL = "sqlite:///debtors.db"  # SQLite база данных в текущей директории
engine = create_engine(DATABASE_URL)

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)