"""
Repositório de acesso a dados para Pedido e ItemPedido.

Camada de persistência que encapsula operações SQL
nas tabelas 'pedidos' e 'itens_pedido' no banco db_pedidos.

Este repositório é usado pelo PedidoService durante a orquestração:
    1. criar_pedido() → Insere pedido com status PENDENTE
    2. criar_item()   → Insere cada item do pedido
    3. buscar_por_id() → Consulta pedido completo para resposta
"""

from sqlalchemy.orm import Session
from models.pedido import Pedido, ItemPedido


class PedidoRepository:
    """
    Repositório para operações CRUD de Pedido e ItemPedido.

    Métodos:
        criar_pedido()   – Insere novo pedido na tabela 'pedidos'
        criar_item()     – Insere item na tabela 'itens_pedido'
        buscar_por_id()  – Busca pedido pelo ID (ou None)
    """

    def __init__(self, db: Session):
        """Recebe a sessão do banco via Dependency Injection do FastAPI."""
        self.db = db

    def criar_pedido(self, pedido: Pedido) -> Pedido:
        """
        Insere um novo pedido no banco de dados.

        Fluxo:
            1. INSERT na tabela 'pedidos' com status PENDENTE
            2. Commit da transação
            3. Refresh para obter o ID gerado
            4. Retorna pedido com ID preenchido

        O status será atualizado depois pelo Service
        (PAGO ou CANCELADO conforme resultado do pagamento).
        """
        self.db.add(pedido)
        self.db.commit()
        self.db.refresh(pedido)
        return pedido

    def criar_item(self, item: ItemPedido):
        """
        Insere um item do pedido no banco de dados.

        Cada item contém: pedido_id, produto_id, nome_produto,
        quantidade, preco_unitario e subtotal.
        É chamado uma vez para cada produto no pedido.
        """
        self.db.add(item)
        self.db.commit()

    def buscar_por_id(self, id: int):
        """
        Busca pedido pelo ID.

        Retorna:
            Pedido se encontrado, None caso contrário.
        Usado pelo endpoint GET /orders/{id} para consulta.
        """
        return self.db.query(Pedido).filter(Pedido.id == id).first()