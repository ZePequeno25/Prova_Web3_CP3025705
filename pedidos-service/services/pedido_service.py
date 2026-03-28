import requests
from sqlalchemy.orm import Session
from repositories.pedido_repository import PedidoRepository
from models.pedido import Pedido, ItemPedido, StatusPedido
from dtos.pedido_dto import PedidoCreate, PedidoResponse, ItemPedidoResponse

class PedidoService:
    """
    Serviço ORQUESTRADOR de pedidos.
    
    Este é o serviço mais importante do sistema! Ele coordena toda a lógica
    de negócio ao criar um pedido, integrando TODOS os outros 4 serviços.
    
    Fluxo de um pedido:
    1. Validar que usuário existe
    2. Validar que todos os produtos têm estoque disponível
    3. Criar o pedido no banco
    4. Buscar dados (nome, preço) de cada produto no Catálogo
    5. Calcular valor total
    6. Baixar estoque de cada item
    7. Processar pagamento
    8. Atualizar status do pedido (PAGO ou CANCELADO)
    
    Integração com serviços:
    - Usuários Service: validar usuário
    - Catálogo Service: obter nome e preço do produto
    - Estoque Service: validar disponibilidade e decrementar
    - Pagamento Service: processar transação
    """
    
    def __init__(self, repository: PedidoRepository, db: Session):
        self.repository = repository
        self.db = db
        # URLs dos outros microserviços
        self.catalogo_url = "http://127.0.0.1:8001"
        self.usuarios_url = "http://127.0.0.1:8002"
        self.estoque_url = "http://127.0.0.1:8004"
        self.pagamento_url = "http://127.0.0.1:8005"

    def criar_pedido(self, dto: PedidoCreate):
        """
        Cria um novo pedido e coordena TODO o fluxo de processamento.
        
        Este é o PRINCIPAL método do sistema. Ele faz orquestração de microsserviços.
        
        ETAPAS REALIZADAS:
        ===================
        
        ETAPA 1: VALIDAÇÃO DO USUÁRIO
        - Verifica se usuário_id existe no serviço de Usuários
        - Se não existir, cancela a operação
        
        ETAPA 2: VERIFICAÇÃO DE ESTOQUE
        - Para cada item do pedido:
          * Consulta Estoque Service para verificar quantidade disponível
          * Valida se há quantidade suficiente
          * Se faltar, informa erro indicando exatamente o quanto falta
        
        ETAPA 3: CRIAÇÃO DO PEDIDO
        - Cria registro no banco com status PENDENTE
        - Gera um ID único para o pedido
        
        ETAPA 4: PROCESSAMENTO DE ITENS
        - Para cada item do pedido:
          * Busca dados do produto no Catálogo (nome, preço)
          * Calcula subtotal (preço x quantidade)
          * Acumula valor total do pedido
          * Cria registro de item_pedido no banco
          * Prepara resposta com dados formatados
        
        ETAPA 5: DECREMENTO DE ESTOQUE
        - Para cada item:
          * Chama Estoque Service para decrementar a quantidade
          * Garante atomicidade (ou tudo é decrementado ou nada é)
        
        ETAPA 6: PROCESSAMENTO DE PAGAMENTO
        - Envia requisição para Pagamento Service com:
          * pedido_id
          * usuario_id
          * valor total calculado
          * método de pagamento
        - Recebe resposta com status APROVADO ou RECUSADO
        
        ETAPA 7: FINALIZAÇÃO DO PEDIDO
        - Se pagamento APROVADO:
          * Status do pedido = PAGO ✅
        - Se pagamento RECUSADO:
          * Status do pedido = CANCELADO ❌
          * Nota: Estoque JÁ foi decrementado (potencial item pendente!)
        
        TRATAMENTO DE ERROS:
        ====================
        - ConnectionError: Se qualquer microserviço não está disponível
        - ValueError: Validações de negócio (usuário não existe, estoque insuficiente, etc)
        - Exception: Outros erros inesperados
        
        Args:
            dto (PedidoCreate): DTO contendo:
                - usuario_id: ID do usuário que faz o pedido
                - itens: Lista de itens com produto_id e quantidade
        
        Returns:
            PedidoResponse: Pedido completo com:
                - id: ID único do pedido
                - usuario_id: ID do usuário
                - status: PAGO ou CANCELADO
                - valor_total: Soma de todos os itens
                - criado_em: Data/hora de criação
                - itens: Lista com detalhes de cada item
        
        Raises:
            ValueError: Se validações falharem (usuário não existe, estoque insuficiente, etc)
            ConnectionError: Se algum microserviço está indisponível
        """
        try:
            # ===== ETAPA 1: VALIDAR USUÁRIO =====
            user_resp = requests.get(f"{self.usuarios_url}/users/{dto.usuario_id}", timeout=5)
            if user_resp.status_code != 200:
                raise ValueError(f"Usuário ID {dto.usuario_id} não encontrado")

            # ===== ETAPA 2: VERIFICAR ESTOQUE DISPONÍVEL =====
            for item in dto.itens:
                estoque_resp = requests.get(f"{self.estoque_url}/inventory/{item.produto_id}", timeout=5)
                if estoque_resp.status_code != 200:
                    raise ValueError(f"Estoque não encontrado para o produto {item.produto_id}")
                
                estoque = estoque_resp.json()
                if estoque["quantidade_disponivel"] < item.quantidade:
                    raise ValueError(
                        f"Estoque insuficiente para produto {item.produto_id}. "
                        f"Disponível: {estoque['quantidade_disponivel']}, Solicitado: {item.quantidade}"
                    )

            # ===== ETAPA 3: CRIAR PEDIDO NO BANCO =====
            pedido = Pedido(usuario_id=dto.usuario_id, valor_total=0.0)
            pedido = self.repository.criar_pedido(pedido)

            valor_total = 0.0
            itens_response = []

            # ===== ETAPA 4: PROCESSAR ITENS E CALCULAR VALOR =====
            for item in dto.itens:
                # Busca informações do produto (nome, preço)
                prod_resp = requests.get(f"{self.catalogo_url}/products/{item.produto_id}", timeout=5)
                if prod_resp.status_code != 200:
                    raise ValueError(f"Produto ID {item.produto_id} não encontrado no Catálogo")

                produto = prod_resp.json()
                if "preco" not in produto:
                    raise ValueError(f"Produto ID {item.produto_id} não possui preço no Catálogo")

                # Calcula subtotal para este item
                subtotal = float(produto["preco"]) * item.quantidade
                valor_total += subtotal

                # Salva item do pedido no banco
                item_pedido = ItemPedido(
                    pedido_id=pedido.id,
                    produto_id=item.produto_id,
                    nome_produto=produto.get("nome"),
                    quantidade=item.quantidade,
                    preco_unitario=float(produto["preco"]),
                    subtotal=subtotal
                )
                self.repository.criar_item(item_pedido)

                # Prepara resposta com dados formatados
                itens_response.append(ItemPedidoResponse(
                    produto_id=item.produto_id,
                    nome_produto=produto.get("nome"),
                    quantidade=item.quantidade,
                    preco_unitario=float(produto["preco"]),
                    subtotal=subtotal
                ))

                # ===== ETAPA 5: DECREMENTAR ESTOQUE =====
                requests.post(
                    f"{self.estoque_url}/inventory/{item.produto_id}/decrement",
                    params={"quantidade": item.quantidade},
                    timeout=5
                )

            # Atualiza o valor total do pedido
            pedido.valor_total = valor_total
            self.repository.criar_pedido(pedido)

            # ===== ETAPA 6: PROCESSAR PAGAMENTO =====
            pagamento_resp = requests.post(
                f"{self.pagamento_url}/payments",
                json={
                    "pedido_id": pedido.id,
                    "usuario_id": dto.usuario_id,
                    "valor": valor_total,
                    "metodo_pagamento": "PIX"  # Pode ser customizado depois
                },
                timeout=5
            )

            if pagamento_resp.status_code != 200:
                erro_msg = pagamento_resp.text if pagamento_resp.text else f"Status {pagamento_resp.status_code}"
                raise ValueError(f"Falha ao processar pagamento: {erro_msg}")

            pagamento = pagamento_resp.json()

            # ===== ETAPA 7: ATUALIZAR STATUS DO PEDIDO =====
            if pagamento["status"] == "APROVADO":
                pedido.status = StatusPedido.PAGO
            else:
                pedido.status = StatusPedido.CANCELADO

            self.repository.criar_pedido(pedido)

            # ===== RETORNAR RESPOSTA =====
            return PedidoResponse(
                id=pedido.id,
                usuario_id=pedido.usuario_id,
                status=pedido.status.value,
                valor_total=pedido.valor_total,
                criado_em=pedido.criado_em,
                itens=itens_response
            )

        except requests.exceptions.ConnectionError:
            raise ValueError("Erro de conexão: verifique se todos os serviços estão rodando")
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Erro ao criar pedido: {str(e)}")