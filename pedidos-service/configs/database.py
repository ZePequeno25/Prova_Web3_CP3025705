"""
Configuração de banco de dados para Pedidos Service.

Gerencia a persistência de pedidos e itens de pedido.
O banco db_pedidos é isolado dos demais serviços,
garantindo que apenas Pedidos Service acesse estes dados.

Tabelas:
- Pedido: ID, usuario_id, status, valor_total, criado_em
- ItemPedido: ID, pedido_id, produto_id, quantidade, preço, subtotal
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# String de conexão para db_pedidos
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria banco db_pedidos se não existir
if not database_exists(engine.url):
    create_database(engine.url)
    print("✅ Banco de dados criado automaticamente!")

# Factory de sessões para Pedidos Service
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos ORM (Pedido, ItemPedido)
Base = declarative_base()

def get_db():
    """
    Dependency Injection para FastAPI.
    Fornece sessão ativa para cada operação de pedido.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Cria tabelas: pedidos e itens_pedido.
    Chamada no lifespan da aplicação.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas automaticamente!")