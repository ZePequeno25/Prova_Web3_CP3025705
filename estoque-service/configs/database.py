"""
Configuração de banco de dados para Estoque Service.

Gerencia o inventário de produtos. O banco db_estoque é isolado
e independente - nenhum outro serviço acessa diretamente.

Tabelas:
- Estoque: produto_id (FK), quantidade_disponível

Segurança:
- Operações de decremento são atômicas
- Validações antes de atualizar
- Produto deve existir no Catálogo antes de ter estoque
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# URL de conexão para db_estoque
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria banco se não existir
if not database_exists(engine.url):
    create_database(engine.url)
    print("✅ Banco criado automaticamente!")

# Factory de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM (Estoque)
Base = declarative_base()

def get_db():
    """
    Dependency Injection para FastAPI.
    Fornece sessão ativa para operações de estoque.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Cria tabela estoque.
    Idempotente e seguro.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas automaticamente!")