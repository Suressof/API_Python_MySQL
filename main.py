from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка подключения к MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/api_db"

# Создание движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Модель таблицы
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    email = Column(String(50), unique=True, index=True)

# Создание таблиц в базе данных (если они ещё не созданы)
Base.metadata.create_all(bind=engine)

# FastAPI приложение
app = FastAPI()

# Pydantic модель для валидации данных
class UserCreate(BaseModel):
    name: str
    email: str

# Эндпоинт для создания пользователя
@app.post("/users/")
def create_user(user: UserCreate):
    db = SessionLocal()
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

# Эндпоинт для получения пользователя по ID
@app.get("/users/{user_id}")
def read_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Эндпоинт для получения всех пользователей
@app.get("/users/")
def read_all_users():
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    return users

# Эндпоинт для удаления пользователя по ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    db.close()
    return {"message": "User deleted"}