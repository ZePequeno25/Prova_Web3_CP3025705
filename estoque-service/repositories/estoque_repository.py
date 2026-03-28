"""
Repositório de acesso a dados para Estoque.

Camada de persistência que encapsula operações SQL
na tabela 'estoque' no banco db_estoque.

Lógica de Upsert:
    - criar_ou_atualizar() funciona como UPSERT:
      se o produto já tem estoque, atualiza a quantidade;
      caso contrário, cria um novo registro.
"""

from sqlalchemy.orm import Session
from models.estoque import Estoque


class EstoqueRepository:
    """
    Repositório para operações CRUD de Estoque.

    Métodos:
        criar_ou_atualizar()  – UPSERT: cria ou atualiza estoque de um produto
        buscar_por_produto()  – Consulta estoque pelo produto_id (ou None)
    """

    def __init__(self, db: Session):
        """Recebe a sessão do banco via Dependency Injection do FastAPI."""
        self.db = db

    def criar_ou_atualizar(self, produto_id: int, quantidade: int) -> Estoque:
        """
        Cria ou atualiza o estoque de um produto (padrão UPSERT).

        Fluxo:
            1. Busca estoque existente para o produto_id
            2. Se encontrou → atualiza quantidade_disponivel (UPDATE)
            3. Se não encontrou → cria novo registro (INSERT)
            4. Commit + refresh para garantir dados atualizados

        Retorna:
            Registro de Estoque atualizado/criado.
        """
        estoque = self.db.query(Estoque).filter(Estoque.produto_id == produto_id).first()
        
        if estoque:
            # Produto já tem estoque — atualiza quantidade
            estoque.quantidade_disponivel = quantidade
        else:
            # Produto sem estoque — cria novo registro
            estoque = Estoque(produto_id=produto_id, quantidade_disponivel=quantidade)
            self.db.add(estoque)
        
        self.db.commit()
        self.db.refresh(estoque)
        return estoque

    def buscar_por_produto(self, produto_id: int):
        """
        Busca estoque pelo produto_id.

        Retorna:
            Estoque se encontrado, None caso contrário.
        Usado pelo Pedidos Service (via REST) para validar disponibilidade
        e pelo endpoint GET /inventory/{productId} para consulta.
        """
        return self.db.query(Estoque).filter(Estoque.produto_id == produto_id).first()