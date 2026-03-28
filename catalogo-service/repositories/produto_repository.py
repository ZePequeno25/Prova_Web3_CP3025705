"""
Repositório de acesso a dados para Produto.

Camada de persistência que encapsula todas as operações SQL
relacionadas à tabela 'produtos' no banco db_catalogo.

Padrão Repository:
    - Isola a lógica de banco do Service
    - Recebe sessão SQLAlchemy via Dependency Injection
    - Cada método executa uma operação atômica no banco
"""

from sqlalchemy.orm import Session
from models.produto import Produto


class ProdutoRepository:
    """
    Repositório para operações CRUD de Produto.

    Métodos:
        criar()          – Insere novo produto no banco
        listar()         – Retorna todos os produtos
        buscar_por_id()  – Busca produto pelo ID (ou None se não encontrado)
    """

    def __init__(self, db: Session):
        """Recebe a sessão do banco via Dependency Injection do FastAPI."""
        self.db = db

    def criar(self, produto: Produto) -> Produto:
        """
        Insere um novo produto no banco de dados.

        Fluxo:
            1. Adiciona o objeto à sessão (INSERT)
            2. Faz commit da transação
            3. Refresh para obter o ID gerado
            4. Retorna o produto com ID preenchido

        Em caso de nome duplicado, o banco lança IntegrityError.
        """
        self.db.add(produto)
        self.db.commit()
        self.db.refresh(produto)
        return produto

    def listar(self):
        """Retorna todos os produtos cadastrados (SELECT * FROM produtos)."""
        return self.db.query(Produto).all()

    def buscar_por_id(self, id: int):
        """
        Busca produto pelo ID.

        Retorna:
            Produto se encontrado, None caso contrário.
        Usado pelo Pedidos Service (via REST) para obter preço unitário.
        """
        return self.db.query(Produto).filter(Produto.id == id).first()