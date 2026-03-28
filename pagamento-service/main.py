"""
Pagamento Service — Ponto de entrada (main.py)

Serviço responsável por simular o processamento de pagamentos.
Roda na porta 8005 e simula uma processadora com taxa de aprovação de 85%.

Endpoints:
    POST /payments → Processa pagamento (simulação)

Integrações:
    - Chamado pelo Pedidos Service (porta 8003) durante o fluxo de compra
    - Retorna status APROVADO (gera transacao_id) ou RECUSADO

Documentação automática:
    Swagger: http://localhost:8005/docs
    Redoc:   http://localhost:8005/redoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from configs.database import create_tables, get_db
from services.pagamento_service import PagamentoService
from repositories.pagamento_repository import PagamentoRepository
from dtos.pagamento_dto import PagamentoCreate, PagamentoResponse


# =============================================
# Lifespan — Inicialização
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handler de ciclo de vida do FastAPI.
    Cria tabela 'pagamentos' ao iniciar o serviço.
    """
    create_tables()  # Cria tabelas no banco se não existirem
    print("✅ Pagamento Service iniciado")
    yield


# Cria a instância FastAPI com título e lifespan
app = FastAPI(title="Pagamento Service", lifespan=lifespan)


# =============================================
# Endpoints REST
# =============================================

@app.post("/payments", response_model=PagamentoResponse)
def processar_pagamento(pagamento: PagamentoCreate, db=Depends(get_db)):
    """
    Processa um pagamento (simulação de processadora).

    Fluxo:
        1. Recebe JSON com pedido_id, usuario_id, valor e metodo_pagamento
        2. Service simula processadora (85% aprovação)
        3. Se aprovado: gera transacao_id único
        4. Se recusado: transacao_id = None
        5. Salva resultado no banco db_pagamento
        6. Retorna PagamentoResponse com status final

    O Pedidos Service usa o campo 'status' da resposta para
    decidir se o pedido será PAGO ou CANCELADO.

    Erros:
        500 – Erro interno no processamento
    """
    try:
        repository = PagamentoRepository(db)  # Injeta sessão no repositório
        service = PagamentoService(repository)  # Injeta repositório no service
        return service.processar_pagamento(
            pedido_id=pagamento.pedido_id,
            usuario_id=pagamento.usuario_id,
            valor=pagamento.valor,
            metodo_pagamento=pagamento.metodo_pagamento
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))