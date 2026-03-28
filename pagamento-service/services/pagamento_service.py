import random
from repositories.pagamento_repository import PagamentoRepository
from models.pagamento import Pagamento, StatusPagamento
from dtos.pagamento_dto import PagamentoResponse

class PagamentoService:
    """
    Serviço de processamento de pagamentos.
    
    Responsável por simular o processamento de transações de pagamento.
    Em produção, integraria com gateways reais (Stripe, PayPal, etc).
    """
    
    def __init__(self, repository: PagamentoRepository):
        self.repository = repository

    def processar_pagamento(self, pedido_id: int, usuario_id: int, valor: float, metodo_pagamento: str):
        """
        Processa um pagamento para um pedido.
        
        Fluxo:
        1. Simula aprovação/rejeição (85% chance de sucesso)
        2. Gera ID de transação se aprovado
        3. Persiste no banco
        4. Retorna DTO com status convertido (Enum -> String)
        
        Simulação:
        - 85% de chance: Status APROVADO ✅
        - 15% de chance: Status RECUSADO ❌
        - Se aprovado: Gera transacao_id único (TX-{pedido_id}-{random})
        
        Utilizado por:
        - Pedidos Service: automaticamente ao criar pedido
        - Teste manual: clientes podem chamar /payments direto
        
        Args:
            pedido_id (int): ID do pedido associado
            usuario_id (int): ID do usuário que faz o pagamento
            valor (float): Valor em reais (ex: 199.80)
            metodo_pagamento (str): Método usado (PIX, CARTAO, BOLETO, etc)
        
        Returns:
            PagamentoResponse: DTO com:
                - id: ID único da transação
                - pedido_id: ID do pedido
                - usuario_id: ID do usuário
                - valor: Valor pago
                - metodo_pagamento: Método utilizado
                - status: APROVADO ou RECUSADO (string)
                - transacao_id: ID único se aprovado, null se recusado
                - criado_em: Data/hora da transação
        
        Example:
            Entrada:
                pedido_id=1, usuario_id=5, valor=199.80, metodo_pagamento="PIX"
            
            Saída (caso aprovado):
            {
                "id": 1,
                "pedido_id": 1,
                "usuario_id": 5,
                "valor": 199.80,
                "metodo_pagamento": "PIX",
                "status": "APROVADO",
                "transacao_id": "TX-1-542389",
                "criado_em": "2026-03-28T10:30:00"
            }
        """
        # ===== SIMULAR APROVAÇÃO/REJEIÇÃO (85% chance de sucesso) =====
        aprovado = random.random() < 0.85

        # Define status e gera transacao_id se aprovado
        status = StatusPagamento.APROVADO if aprovado else StatusPagamento.RECUSADO
        transacao_id = f"TX-{pedido_id}-{random.randint(100000, 999999)}" if aprovado else None

        # ===== CRIAR REGISTRO DE PAGAMENTO =====
        pagamento = Pagamento(
            pedido_id=pedido_id,
            usuario_id=usuario_id,
            valor=valor,
            metodo_pagamento=metodo_pagamento.upper(),  # Normaliza para MAIÚSCULAS
            status=status,
            transacao_id=transacao_id
        )

        # ===== PERSISTIR NO BANCO =====
        resultado = self.repository.criar(pagamento)
        
        # ===== RETORNAR DTO COM STATUS CONVERTIDO =====
        # Converte Enum para string (importante para JSON!)
        return PagamentoResponse(
            id=resultado.id,
            pedido_id=resultado.pedido_id,
            usuario_id=resultado.usuario_id,
            valor=resultado.valor,
            metodo_pagamento=resultado.metodo_pagamento,
            status=resultado.status.value,  # Enum.value = "APROVADO" ou "RECUSADO"
            transacao_id=resultado.transacao_id,
            criado_em=resultado.criado_em
        )