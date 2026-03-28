"""
Repositório de acesso a dados para Pagamento.

Camada de persistência que encapsula operações SQL
na tabela 'pagamentos' no banco db_pagamento.

Cada chamada ao criar() registra uma tentativa de pagamento
com o resultado da simulação (APROVADO ou RECUSADO).
"""

from sqlalchemy.orm import Session
from models.pagamento import Pagamento


class PagamentoRepository:
    """
    Repositório para operações de persistência de Pagamento.

    Métodos:
        criar()  – Insere novo registro de pagamento no banco
    """

    def __init__(self, db: Session):
        """Recebe a sessão do banco via Dependency Injection do FastAPI."""
        self.db = db

    def criar(self, pagamento: Pagamento) -> Pagamento:
        """
        Insere um novo pagamento no banco de dados.

        Fluxo:
            1. Adiciona o objeto à sessão (INSERT)
            2. Faz commit da transação
            3. Refresh para obter o ID gerado
            4. Retorna o pagamento com ID e status preenchidos

        O status (APROVADO/RECUSADO) e transacao_id já vem
        definidos pelo PagamentoService antes de chamar este método.
        """
        self.db.add(pagamento)
        self.db.commit()
        self.db.refresh(pagamento)
        return pagamento