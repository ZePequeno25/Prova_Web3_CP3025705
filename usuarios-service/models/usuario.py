"""
Modelo ORM para a tabela 'usuarios' no banco db_usuarios.

Representa um usuário do sistema de e-commerce.
A senha é armazenada como hash bcrypt (nunca em texto puro).
O Pedidos Service consulta este modelo (via REST) para validar o usuário antes de criar pedidos.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from configs.database import Base
from datetime import datetime


class Usuario(Base):
    """
    Entidade Usuario — mapeada para a tabela 'usuarios'.

    Campos:
        id         – Chave primária auto-incrementada
        nome       – Nome completo do usuário (máx. 100 caracteres)
        email      – E-mail único, usado como identificador (indexado)
        senha      – Hash bcrypt da senha (máx. 255 caracteres)
        ativo      – Flag de ativação da conta (default: True)
        criado_em  – Data/hora de criação automática (UTC)

    Segurança:
        - A senha NUNCA é armazenada em texto puro
        - O hash é gerado no UsuarioService com bcrypt
        - O UsuarioResponse DTO exclui a senha da resposta JSON
    """
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)                          # PK auto-incrementada
    nome = Column(String(100), nullable=False)                                   # Nome completo
    email = Column(String(100), unique=True, nullable=False, index=True)         # E-mail único (indexado para buscas rápidas)
    senha = Column(String(255), nullable=False)                                  # Hash bcrypt da senha
    ativo = Column(Boolean, default=True)                                        # Conta ativa/inativa
    criado_em = Column(DateTime, default=datetime.utcnow)                        # Timestamp de criação