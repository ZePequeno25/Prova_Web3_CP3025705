from fastapi import FastAPI, Depends
from configs.database import create_tables, get_db
from services.produto_service import ProdutoService
from repositories.produto_repository import ProdutoRepository
from dtos.produto_dto import ProdutoCreate, ProdutoResponse

app = FastAPI(title="Catálogo Service")

# Cria banco e tabelas na primeira execução
@app.on_event("startup")
def startup_event():
    create_tables()

@app.post("/products", response_model=ProdutoResponse)
def criar_produto(produto: ProdutoCreate, db=Depends(get_db)):
    repository = ProdutoRepository(db)
    service = ProdutoService(repository)
    return service.criar_produto(produto)

@app.get("/products")
def listar_produtos(db=Depends(get_db)):
    repository = ProdutoRepository(db)
    service = ProdutoService(repository)
    return service.listar_produtos()

@app.get("/products/{id}")
def buscar_produto(id: int, db=Depends(get_db)):
    repository = ProdutoRepository(db)
    service = ProdutoService(repository)
    produto = service.buscar_por_id(id)
    if not produto:
        return {"erro": "Produto não encontrado"}
    return produto