"""
Estoque Service — Ponto de entrada (main.py)

Serviço responsável pelo controle de inventário de produtos.
Roda na porta 8004 e gerencia quantidades disponíveis em estoque.

Endpoints:
    GET  /inventory/{productId}           → Consulta estoque de um produto
    PUT  /inventory/{productId}           → Atualiza quantidade em estoque
    POST /inventory/{productId}/decrement → Decrementa estoque (usado pelo Pedidos Service)

Integrações:
    - Valida existência do produto no Catálogo Service (porta 8001)
    - Pedidos Service chama GET e POST /decrement durante o fluxo de compra

Documentação automática:
    Swagger: http://localhost:8004/docs
    Redoc:   http://localhost:8004/redoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Query
from configs.database import create_tables, get_db
from services.estoque_service import EstoqueService
from repositories.estoque_repository import EstoqueRepository
from dtos.estoque_dto import EstoqueResponse


# =============================================
# Lifespan — Inicialização
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handler de ciclo de vida do FastAPI.
    Cria tabela 'estoque' ao iniciar o serviço.
    """
    create_tables()  # Cria tabelas no banco se não existirem
    print("✅ Estoque Service iniciado - Tabelas verificadas/criadas")
    yield


# Cria a instância FastAPI com título e lifespan
app = FastAPI(title="Estoque Service", lifespan=lifespan)


# =============================================
# Endpoints REST
# =============================================

@app.get("/inventory/{productId}", response_model=EstoqueResponse)
def consultar_estoque(productId: int, db=Depends(get_db)):
    """
    Consulta a quantidade disponível em estoque de um produto.

    Parâmetros:
        productId – ID do produto no Catálogo Service

    Retorna:
        EstoqueResponse com produto_id, quantidade e data de atualização.

    Erros:
        404 – Produto não encontrado no estoque
    """
    try:
        repository = EstoqueRepository(db)
        service = EstoqueService(repository)
        return service.consultar_estoque(productId)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.put("/inventory/{productId}")
def atualizar_estoque(productId: int, quantidade: int, db=Depends(get_db)):
    """
    Atualiza (ou cria) o estoque de um produto.

    Parâmetros:
        productId  – ID do produto
        quantidade – Nova quantidade disponível (query string)

    Exemplo: PUT /inventory/1?quantidade=50

    Erros:
        400 – Produto não existe no Catálogo ou dados inválidos
    """
    try:
        repository = EstoqueRepository(db)
        service = EstoqueService(repository)
        return service.atualizar_estoque(productId, quantidade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Endpoint interno — usado pelo Pedidos Service durante o fluxo de compra
@app.post("/inventory/{productId}/decrement")
def decrementar_estoque(productId: int, quantidade: int = Query(..., gt=0), db=Depends(get_db)):
    """
    Decrementa atomicamente o estoque de um produto.

    Parâmetros:
        productId  – ID do produto a decrementar
        quantidade – Quantidade a subtrair (deve ser > 0, via query string)

    Exemplo: POST /inventory/1/decrement?quantidade=2

    Fluxo:
        1. Verifica se existe estoque para o produto
        2. Verifica se quantidade disponível é suficiente
        3. Subtrai e salva no banco

    Erros:
        400 – Estoque insuficiente ou produto sem estoque
    """
    try:
        repository = EstoqueRepository(db)
        service = EstoqueService(repository)
        resultado = service.decrementar_estoque(productId, quantidade)
        return {"mensagem": "Estoque decrementado com sucesso", "novo_estoque": resultado.quantidade_disponivel}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))