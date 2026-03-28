"""
Usuários Service — Ponto de entrada (main.py)

Serviço responsável pelo gerenciamento de usuários do e-commerce.
Roda na porta 8002 e fornece endpoints REST para criar e consultar usuários.

Endpoints:
    POST /users      → Registra novo usuário (senha criptografada com bcrypt)
    GET  /users/{id} → Busca usuário por ID (usado pelo Pedidos Service)

Segurança:
    - Senha criptografada com bcrypt antes de salvar
    - Response DTO exclui campo senha

Documentação automática:
    Swagger: http://localhost:8002/docs
    Redoc:   http://localhost:8002/redoc
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from configs.database import create_tables, get_db
from services.usuario_service import UsuarioService
from repositories.usuario_repository import UsuarioRepository
from dtos.usuario_dto import UsuarioCreate, UsuarioResponse


# =============================================
# Lifespan — Inicialização e Encerramento
# =============================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handler de ciclo de vida do FastAPI.
    Cria tabelas no banco ao iniciar o serviço.
    """
    create_tables()  # Cria tabelas no banco se não existirem
    print("✅ Pedidos Service iniciado - Tabelas verificadas/criadas")
    yield
    print("🛑 Pedidos Service encerrado")


# Cria a instância FastAPI com título e lifespan
app = FastAPI(title="Pedidos Service", lifespan=lifespan)


# =============================================
# Endpoints REST
# =============================================

@app.post("/users", response_model=UsuarioResponse)
def criar_usuario(usuario: UsuarioCreate, db=Depends(get_db)):
    """
    Registra um novo usuário no sistema.

    Fluxo:
        1. Recebe JSON com nome, email e senha
        2. Service criptografa senha com bcrypt
        3. Repository salva no banco db_usuarios
        4. Retorna usuário SEM o campo senha (UsuarioResponse)

    Erros:
        400 – E-mail já cadastrado
        500 – Erro interno do servidor
    """
    try:
        repository = UsuarioRepository(db)  # Injeta sessão no repositório
        service = UsuarioService(repository)  # Injeta repositório no service
        return service.criar_usuario(usuario)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")


@app.get("/users/{id}", response_model=UsuarioResponse)
def buscar_usuario(id: int, db=Depends(get_db)):
    """
    Busca um usuário específico pelo ID.

    Usado internamente pelo Pedidos Service para validar
    que o usuário existe antes de criar um pedido.

    Erros:
        404 – Usuário não encontrado
    """
    repository = UsuarioRepository(db)
    service = UsuarioService(repository)
    usuario = service.buscar_por_id(id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario