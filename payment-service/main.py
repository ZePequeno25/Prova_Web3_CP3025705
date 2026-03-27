from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from datetime import datetime
import uvicorn, os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@mysql:3306/ecommerce_payment"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class PaymentDB(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pedido_id = Column(Integer, nullable=False)
    usuario_id = Column(Integer, nullable=False)
    valor = Column(Float, nullable=False)
    metodo_pagamento = Column(String(50))
    status = Column(String(20))
    criado_em = Column(String(30))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Payment Service")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

class PaymentRequest(BaseModel):
    pedido_id: int
    usuario_id: int
    valor: float
    metodo_pagamento: str = "PIX"

@app.post("/payments")
def processar_pagamento(payment: PaymentRequest, db: Session = Depends(get_db)):
    novo = PaymentDB(
        pedido_id=payment.pedido_id,
        usuario_id=payment.usuario_id,
        valor=payment.valor,
        metodo_pagamento=payment.metodo_pagamento,
        status="APROVADO",
        criado_em=datetime.now().isoformat()
    )
    db.add(novo)
    db.commit()
    return {"status": "APROVADO"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)