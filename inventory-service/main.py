from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
import uvicorn, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@mysql:3306/ecommerce_inventory"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class InventoryDB(Base):
    __tablename__ = "inventory"
    product_id = Column(Integer, primary_key=True)
    quantidade = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Service")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class InventoryUpdate(BaseModel):
    quantidade: int

@app.get("/inventory/{product_id}")
def consultar_estoque(product_id: int, db: Session = Depends(get_db)):
    inv = db.query(InventoryDB).filter(InventoryDB.product_id == product_id).first()
    return {"quantidade": inv.quantidade if inv else 0}

@app.put("/inventory/{product_id}")
def atualizar_estoque(product_id: int, update: InventoryUpdate, db: Session = Depends(get_db)):
    inv = db.query(InventoryDB).filter(InventoryDB.product_id == product_id).first()
    if not inv:
        inv = InventoryDB(product_id=product_id, quantidade=update.quantidade)
        db.add(inv)
    else:
        inv.quantidade = update.quantidade
    db.commit()
    return {"message": "Estoque atualizado", "quantidade": update.quantidade}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)