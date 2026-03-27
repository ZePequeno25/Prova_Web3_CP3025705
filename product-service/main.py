from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List
import uvicorn, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@mysql:3306/ecommerce_product"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ProductDB(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(String(500))
    preco = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Product Service")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class ProductCreate(BaseModel):
    nome: str
    descricao: str
    preco: float

class Product(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    ativo: bool

@app.post("/products", response_model=Product)
def cadastrar_produto(prod: ProductCreate, db: Session = Depends(get_db)):
    novo = ProductDB(**prod.model_dump(), ativo=True)
    db.add(novo); db.commit(); db.refresh(novo)
    return novo

@app.get("/products", response_model=List[Product])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(ProductDB).all()

@app.get("/products/{product_id}", response_model=Product)
def obter_produto(product_id: int, db: Session = Depends(get_db)):
    prod = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not prod: raise HTTPException(404, "Produto não encontrado")
    return prod