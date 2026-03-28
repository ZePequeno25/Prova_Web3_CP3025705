"""
Catálogo Service — Ponto de entrada (main.py)

Serviço responsável pelo gerenciamento de produtos do e-commerce.
Roda na porta 8001 e fornece endpoints REST para CRUD de produtos.

Endpoints:
    POST /products      → Cadastra novo produto
    GET  /products      → Lista todos os produtos
    GET  /products/{id} → Busca produto por ID (usado pelo Pedidos Service)

Documentação automática:
    Swagger: http://localhost:8001/docs
    Redoc:   http://localhost:8001/redoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from configs.database import create_tables, get_db
from services.produto_service import ProdutoService
from repositories.produto_repository import ProdutoRepository
from dtos.produto_dto import ProdutoCreate, ProdutoResponse
from sqlalchemy.exc import IntegrityError


# =============================================
# Lifespan — Inicialização e Encerramento
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handler de ciclo de vida do FastAPI.
    Substitui os decorators @app.on_event('startup') e @app.on_event('shutdown').
    """
    # Código executado ao INICIAR a aplicação
    create_tables()  # Cria tabelas no banco se não existirem
    print("✅ Pedidos Service iniciado - Tabelas verificadas/criadas")
    yield
    # Código executado ao ENCERRAR a aplicação (opcional)
    print("🛑 Pedidos Service encerrado")


# Cria a instância FastAPI com título e lifespan
app = FastAPI(title="Pedidos Service", lifespan=lifespan)


# =============================================
# Endpoints REST
# =============================================

@app.post("/products", response_model=ProdutoResponse)
def criar_produto(produto: ProdutoCreate, db=Depends(get_db)):
    """
    Cadastra um novo produto no catálogo.

    Recebe JSON com nome, descricao (opcional) e preco.
    Retorna o produto criado com ID e timestamp.

    Erros:
        400 – Nome duplicado ou dados inválidos
        500 – Erro interno do servidor
    """
    try:
        repository = ProdutoRepository(db)  # Injeta sessão no repositório
        service = ProdutoService(repository)  # Injeta repositório no service
        return service.criar_produto(produto)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/products")
def listar_produtos(db=Depends(get_db)):
    """
    Lista todos os produtos cadastrados no catálogo.

    Retorna array JSON com todos os produtos ativos.
    """
    repository = ProdutoRepository(db)
    service = ProdutoService(repository)
    return service.listar_produtos()


@app.get("/products/{id}")
def buscar_produto(id: int, db=Depends(get_db)):
    """
    Busca um produto específico pelo ID.

    Usado internamente pelo Pedidos Service para obter
    nome e preço unitário durante a criação de pedidos.

    Erros:
        404 – Produto não encontrado
    """
    repository = ProdutoRepository(db)
    service = ProdutoService(repository)
    produto = service.buscar_por_id(id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto