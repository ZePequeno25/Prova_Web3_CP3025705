from sqlalchemy.orm import Session
from models.produto import Produto

class ProdutoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, produto: Produto) -> Produto:
        self.db.add(produto)
        self.db.commit()
        self.db.refresh(produto)
        return produto

    def listar(self):
        return self.db.query(Produto).all()

    def buscar_por_id(self, id: int):
        return self.db.query(Produto).filter(Produto.id == id).first()