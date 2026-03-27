from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
import uvicorn, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@mysql:3306/ecommerce_user"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class UserCreate(BaseModel):
    nome: str
    email: str
    senha: str

class UserResponse(BaseModel):
    id: int
    nome: str
    email: str

@app.post("/users", response_model=UserResponse)
def cadastrar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    novo = UserDB(nome=user.nome, email=user.email, senha=user.senha)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return UserResponse(id=novo.id, nome=novo.nome, email=novo.email)

@app.get("/users/{user_id}", response_model=UserResponse)
def obter_usuario(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return UserResponse(id=user.id, nome=user.nome, email=user.email)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)