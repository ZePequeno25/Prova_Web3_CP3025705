from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, Float, String, JSON
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List
from datetime import datetime
import requests, uvicorn, os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@mysql:3306/ecommerce_order"
PRODUCT_URL = os.getenv("PRODUCT_URL", "http://product-service:8001")
INVENTORY_URL = os.getenv("INVENTORY_URL", "http://inventory-service:8004")
PAYMENT_URL = os.getenv("PAYMENT_URL", "http://payment-service:8005")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(Integer, nullable=False)
    status = Column(String(20))
    valor_total = Column(Float)
    criado_em = Column(String(30))
    itens = Column(JSON)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Order Service")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class ItemCreate(BaseModel):
    produto_id: int
    quantidade: int

class OrderCreate(BaseModel):
    usuario_id: int
    itens: List[ItemCreate]

class OrderItem(BaseModel):
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: float
    subtotal: float

class OrderResponse(BaseModel):
    id: int
    usuario_id: int
    status: str
    valor_total: float
    criado_em: str
    itens: List[OrderItem]

@app.post("/orders", response_model=OrderResponse)
def criar_pedido(order: OrderCreate, db: Session = Depends(get_db)):
    itens_enriquecidos = []
    valor_total = 0.0

    for item in order.itens:
        r_prod = requests.get(f"{PRODUCT_URL}/products/{item.produto_id}")
        if r_prod.status_code != 200:
            raise HTTPException(404, f"Produto {item.produto_id} não encontrado")
        prod = r_prod.json()

        r_inv = requests.get(f"{INVENTORY_URL}/inventory/{item.produto_id}")
        estoque = r_inv.json()["quantidade"]
        if estoque < item.quantidade:
            raise HTTPException(400, f"Estoque insuficiente para produto {item.produto_id}")

        subtotal = prod["preco"] * item.quantidade
        valor_total += subtotal

        itens_enriquecidos.append({
            "produto_id": item.produto_id,
            "nome_produto": prod["nome"],
            "quantidade": item.quantidade,
            "preco_unitario": prod["preco"],
            "subtotal": subtotal
        })

    pedido = OrderDB(
        usuario_id=order.usuario_id,
        status="CRIADO",
        valor_total=valor_total,
        criado_em=datetime.now().isoformat(),
        itens=itens_enriquecidos
    )
    db.add(pedido)
    db.commit()
    db.refresh(pedido)
    pedido_id = pedido.id

    # Pagamento
    pay_payload = {
        "pedido_id": pedido_id,
        "usuario_id": order.usuario_id,
        "valor": valor_total,
        "metodo_pagamento": "PIX"
    }
    r_pay = requests.post(f"{PAYMENT_URL}/payments", json=pay_payload)
    status_pag = r_pay.json().get("status", "RECUSADO")

    if status_pag == "APROVADO":
        pedido.status = "PAGO"
        # Baixa estoque
        for item in itens_enriquecidos:
            r_inv = requests.get(f"{INVENTORY_URL}/inventory/{item['produto_id']}")
            novo_estoque = r_inv.json()["quantidade"] - item["quantidade"]
            requests.put(f"{INVENTORY_URL}/inventory/{item['produto_id']}", json={"quantidade": novo_estoque})
    else:
        pedido.status = "CANCELADO"

    db.commit()
    return OrderResponse(id=pedido.id, **{k: v for k, v in pedido.__dict__.items() if k not in ["_sa_instance_state", "itens"]}, itens=itens_enriquecidos)

@app.get("/orders/{order_id}", response_model=OrderResponse)
def consultar_pedido(order_id: int, db: Session = Depends(get_db)):
    pedido = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not pedido:
        raise HTTPException(404, "Pedido não encontrado")
    return OrderResponse(id=pedido.id, **{k: v for k, v in pedido.__dict__.items() if k not in ["_sa_instance_state", "itens"]}, itens=pedido.itens)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)