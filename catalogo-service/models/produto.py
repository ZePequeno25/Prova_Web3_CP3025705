from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from configs.database import Base
from datetime import datetime

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(String(500))
    preco = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime, default=datetime.utcnow)