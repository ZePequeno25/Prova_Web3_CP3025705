from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProdutoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: float

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    preco: float
    ativo: bool
    criado_em: datetime

    class Config:
        from_attributes = True