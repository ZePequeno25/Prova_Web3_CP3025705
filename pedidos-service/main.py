"""
Pedidos Service — Ponto de entrada (main.py)

Serviço CENTRAL que orquestra todo o fluxo de compra do e-commerce.
Roda na porta 8003 e coordena chamadas REST para os outros 4 serviços.

Endpoints:
    POST /orders      → Cria pedido (orquestra Usuários, Estoque, Catálogo e Pagamento)
    GET  /orders/{id} → Consulta pedido completo com itens

Fluxo de Orquestração (POST /orders):
    1. Valida usuário no Usuários Service (porta 8002)
    2. Verifica estoque no Estoque Service (porta 8004)
    3. Cria pedido PENDENTE no banco local
    4. Busca preços no Catálogo Service (porta 8001)
    5. Decrementa estoque no Estoque Service (porta 8004)
    6. Processa pagamento no Pagamento Service (porta 8005)
    7. Atualiza status: PAGO (aprovado) ou CANCELADO (recusado)

Documentação automática:
    Swagger: http://localhost:8003/docs
    Redoc:   http://localhost:8003/redoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from configs.database import create_tables, get_db
from services.pedido_service import PedidoService
from repositories.pedido_repository import PedidoRepository
from dtos.pedido_dto import PedidoCreate, PedidoResponse


# =============================================
# Lifespan — Inicialização
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handler de ciclo de vida do FastAPI.
    Cria tabelas 'pedidos' e 'itens_pedido' ao iniciar.
    """
    create_tables()  # Cria tabelas no banco se não existirem
    print("✅ Pedidos Service iniciado - Tabelas verificadas/criadas")
    yield


# Cria a instância FastAPI com título e lifespan
app = FastAPI(title="Pedidos Service", lifespan=lifespan)


# =============================================
# Endpoints REST
# =============================================

@app.post("/orders", response_model=PedidoResponse)
def criar_pedido(pedido: PedidoCreate, db=Depends(get_db)):
    """
    Cria um novo pedido.
    
    Orquestra todo o fluxo: valida usuário e estoque, registra pedido,
    processa pagamento e retorna pedido com status final (PAGO ou CANCELADO).
    """
    try:
        repository = PedidoRepository(db)
        service = PedidoService(repository, db)
        return service.criar_pedido(pedido)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar pedido: {str(e)}")

@app.get("/orders/{id}", response_model=PedidoResponse)
def consultar_pedido(id: int, db=Depends(get_db)):
    """
    Consulta os detalhes de um pedido específico pelo ID.
    
    Retorna informações completas do pedido incluindo:
    - ID, usuario_id, status (PAGO/CANCELADO)
    - valor_total, data de criação
    - Lista de itens com nome, quantidade, preço unitário e subtotal
    
    Raises:
        404: Se o pedido não foi encontrado
    """
    try:
        repository = PedidoRepository(db)
        pedido = repository.buscar_por_id(id)
        
        if not pedido:
            raise HTTPException(status_code=404, detail=f"Pedido ID {id} não encontrado")
        
        return PedidoResponse(
            id=pedido.id,
            usuario_id=pedido.usuario_id,
            status=pedido.status.value,
            valor_total=pedido.valor_total,
            criado_em=pedido.criado_em,
            itens=[
                {
                    "produto_id": item.produto_id,
                    "nome_produto": item.nome_produto,
                    "quantidade": item.quantidade,
                    "preco_unitario": item.preco_unitario,
                    "subtotal": item.subtotal
                }
                for item in pedido.itens
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar pedido: {str(e)}")