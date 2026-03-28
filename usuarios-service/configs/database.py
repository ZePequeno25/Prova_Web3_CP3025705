"""
Configuração de banco de dados para Usuários Service.

Gerencia a persistência de usuários do sistema.
Cada serviço tem seu próprio banco (db_usuarios),
garantindo isolamento de dados conforme microsserviços.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# URL de conexão específica para este serviço (db_usuarios)
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria banco se não existir
if not database_exists(engine.url):
    create_database(engine.url)
    print("✅ Banco de dados criado automaticamente!")

# Factory de sessões para Usuários Service
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM (Usuario)
Base = declarative_base()

def get_db():
    """
    Dependency Injection para FastAPI.
    Fornece sessão ativa para operações com usuários.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Cria tabela usuarios no banco.
    Idempotente - seguro chamar múltiplas vezes.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas automaticamente!")