"""
Configuração de banco de dados para Catálogo Service.

Este arquivo centraliza toda a configuração do SQLAlchemy e gerenciamento
de sessões. Responsável por:
- Conectar ao MySQL (db_catalogo)
- Criar banco automaticamente se não existir
- Fornecer sessões para operações CRUD
- Criar tabelas automaticamente na inicialização
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# URL de conexão ao banco (ex: mysql+pymysql://user:pass@host/db_catalogo)
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine SQLAlchemy - responsável pela conexão com o banco
engine = create_engine(DATABASE_URL)

# Cria banco automaticamente se não existir
# Importante para inicialização rápida sem scripts SQL manuais
if not database_exists(engine.url):
    create_database(engine.url)
    print("✅ Banco de dados criado automaticamente!")

# SessionLocal: factory para criar novas sessões de conexão
# autocommit=False: transações explícitas (mais seguro)
# autoflush=False: flush manual (controle melhor)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: classe base para todos os modelos ORM
# Todos os modelos devem herdar de Base para serem mapeados
Base = declarative_base()

def get_db():
    """
    Dependency Injection para FastAPI.
    
    Fornece uma sessão de banco de dados para cada requisição.
    Garante que a conexão seja fechada corretamente após uso.
    
    Yields:
        Session: Sessão SQLAlchemy ativa
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Fecha a conexão após a requisição
        db.close()

def create_tables():
    """
    Cria todas as tabelas no banco de dados.
    
    Inspeciona todos os modelos que herdam de Base
    e cria suas respectivas tabelas no banco.
    
    Garantias:
    - Idempotente (seguro chamar múltiplas vezes)
    - Não remove tabelas existentes
    - Apenas cria tabelas que não existem
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas automaticamente!")