from repositories.usuario_repository import UsuarioRepository
from models.usuario import Usuario
from dtos.usuario_dto import UsuarioCreate
from utils.security import hash_senha

class UsuarioService:
    """
    Serviço de gerenciamento de usuários.
    Responsável por autenticação, cadastro e consulta de usuários.
    """
    
    def __init__(self, repository: UsuarioRepository):
        self.repository = repository

    def criar_usuario(self, dto: UsuarioCreate) -> Usuario:
        """
        Cria um novo usuário no sistema.
        
        Fluxo:
        1. Recebe dados do usuário (nome, email, senha)
        2. Criptografa a senha usando bcrypt
        3. Salva apenas o hash da senha (NUNCA em texto plano)
        4. Salva usuário no banco de dados
        5. Retorna usuário criado sem a senha
        
        Segurança:
        - Senha é criptografada irreversivelmente com bcrypt
        - Apenas o hash é armazenado no banco
        - Senha original nunca é salva ou transmitida em texto plano
        
        Utilizado por:
        - Pedidos Service: para validar se usuário existe
        
        Args:
            dto (UsuarioCreate): DTO com dados (nome, email, senha)
        
        Returns:
            Usuario: Usuário criado com ID
        """
        # Criptografa a senha antes de salvar
        senha_hashed = hash_senha(dto.senha)

        usuario = Usuario(
            nome=dto.nome,
            email=dto.email,
            senha=senha_hashed          # Salva apenas o hash criptografado
        )
        return self.repository.criar(usuario)

    def buscar_por_id(self, id: int):
        """
        Busca um usuário específico pelo ID.
        
        Utilizado por:
        - Pedidos Service: para validar existência de usuário antes de criar pedido
        - Autenticação: para recuperar dados do usuário
        
        Args:
            id (int): ID do usuário a buscar
        
        Returns:
            Usuario: Dados do usuário (nome, email, sem senha plain)
        """
        return self.repository.buscar_por_id(id)