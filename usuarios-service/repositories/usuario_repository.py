"""
Repositório de acesso a dados para Usuário.

Camada de persistência que encapsula todas as operações SQL
relacionadas à tabela 'usuarios' no banco db_usuarios.

Segurança:
    - Trata IntegrityError para e-mails duplicados
    - Faz rollback automático em caso de erro
    - Lança ValueError com mensagem amigável ao usuário
"""

from sqlalchemy.orm import Session
from models.usuario import Usuario
from sqlalchemy.exc import IntegrityError


class UsuarioRepository:
    """
    Repositório para operações CRUD de Usuário.

    Métodos:
        criar()          – Insere novo usuário (com tratamento de duplicidade)
        buscar_por_id()  – Busca usuário pelo ID (ou None se não encontrado)
    """

    def __init__(self, db: Session):
        """Recebe a sessão do banco via Dependency Injection do FastAPI."""
        self.db = db

    def criar(self, usuario: Usuario) -> Usuario:
        """
        Insere um novo usuário no banco de dados.

        Fluxo:
            1. Adiciona o objeto à sessão (INSERT)
            2. Faz commit da transação
            3. Refresh para obter o ID gerado
            4. Retorna o usuário com ID preenchido

        Tratamento de erro:
            - Se o e-mail já existir no banco, o MySQL lança IntegrityError
            - O repositório faz rollback e lança ValueError para o Service
            - O main.py converte ValueError em HTTP 400
        """
        try:
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(usuario)
            return usuario
        except IntegrityError:
            self.db.rollback()  # Desfaz a transação pendente
            raise ValueError("Já existe um usuário com este email")

    def buscar_por_id(self, id: int):
        """
        Busca usuário pelo ID.

        Retorna:
            Usuario se encontrado, None caso contrário.
        Usado pelo Pedidos Service (via REST) para validar existência do usuário.
        """
        return self.db.query(Usuario).filter(Usuario.id == id).first()