"""
DTOs (Data Transfer Objects) para o Usuários Service.

Definem os contratos de entrada e saída da API REST.
Usam Pydantic para validação automática:
    - UsuarioCreate   → Dados para registro de novo usuário (entrada)
    - UsuarioResponse  → Dados retornados ao cliente (saída — SEM senha)

Segurança:
    - A senha é recebida no Create mas NUNCA retornada no Response
    - EmailStr valida formato de e-mail automaticamente
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UsuarioCreate(BaseModel):
    """
    DTO de entrada para criação de usuário.

    Campos:
        nome  – Nome completo do usuário (obrigatório)
        email – E-mail válido (validado pelo EmailStr do Pydantic)
        senha – Senha em texto puro (será criptografada com bcrypt no Service)

    Exemplo JSON:
        {"nome": "Maria", "email": "maria@email.com", "senha": "123456"}
    """
    nome: str
    email: EmailStr         # Valida formato de e-mail automaticamente
    senha: str              # Texto puro — será convertido para hash bcrypt


class UsuarioResponse(BaseModel):
    """
    DTO de saída para resposta da API.

    IMPORTANTE: Não inclui o campo 'senha' por segurança.
    O cliente nunca recebe a senha ou hash do usuário.

    Campos:
        id        – ID gerado pelo banco (auto-increment)
        nome      – Nome completo do usuário
        email     – E-mail do usuário
        ativo     – Status da conta (True/False)
        criado_em – Data/hora de criação (UTC)
    """
    id: int
    nome: str
    email: EmailStr
    ativo: bool
    criado_em: datetime

    class Config:
        # Permite converter objetos SQLAlchemy diretamente para DTO
        from_attributes = True