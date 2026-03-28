"""
Configuração de banco de dados para Pagamento Service.

Gerencia transações de pagamento com simulação de processadora.
Banco db_pagamento é isolado - apenas este serviço acessa.

Tabelas:
- Pagamento: pedido_id (FK), metodo_pagamento, status (APROVADO/RECUSADO), transacao_id

Funcionalidades:
- Simula processadora com taxa de aprovação 85%
- Registra cada tentativa com data/hora
- Gera transacao_id apenas para pagamentos aprovados
- Retorna DTO com conversão Enum→String para JSON
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# URL de conexão para db_pagamento
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria banco se não existir
if not database_exists(engine.url):
    create_database(engine.url)
    print("✅ Banco de dados criado automaticamente!")

# Factory de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM (Pagamento)
Base = declarative_base()

def get_db():
    """
    Dependency Injection para FastAPI.
    Fornece sessão ativa para operações de pagamento.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Cria tabela pagamento.
    Idempotente e seguro.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas automaticamente!")