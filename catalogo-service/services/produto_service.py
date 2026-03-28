from repositories.produto_repository import ProdutoRepository
from models.produto import Produto
from dtos.produto_dto import ProdutoCreate
from sqlalchemy.exc import IntegrityError

class ProdutoService:
    """
    Serviço de gerenciamento de produtos do Catálogo.
    Responsável por criar, listar e buscar produtos.
    """
    
    def __init__(self, repository: ProdutoRepository):
        self.repository = repository

    def criar_produto(self, dto: ProdutoCreate) -> Produto:
        """
        Cria um novo produto no catálogo.
        
        Fluxo:
        1. Recebe dados do produto (nome, descrição, preço)
        2. Cria objeto Produto
        3. Salva no banco de dados via repository
        4. Retorna o produto criado com ID
        
        Validações:
        - Nome deve ser único (IntegrityError lançada se duplicado)
        
        Args:
            dto (ProdutoCreate): DTO com dados do produto (nome, descrição, preço)
        
        Returns:
            Produto: Objeto produto com ID gerado
        
        Raises:
            ValueError: Se nome já existe
            Exception: Outros erros de criação
        """
        try:
            produto = Produto(
                nome=dto.nome,
                descricao=dto.descricao,
                preco=dto.preco
            )
            return self.repository.criar(produto)
        
        except IntegrityError:
            raise ValueError(f"Já existe um produto cadastrado com o nome '{dto.nome}'")
        except Exception as e:
            raise Exception(f"Erro ao criar produto: {str(e)}")

    def listar_produtos(self):
        """
        Lista todos os produtos cadastrados no catálogo.
        
        Retorna:
            List[Produto]: Lista de todos os produtos ativos
        """
        return self.repository.listar()

    def buscar_por_id(self, id: int):
        """
        Busca um produto específico pelo ID.
        
        Utilizado por:
        - Pedidos Service: para obter preço do produto
        - Outros serviços: para validar existência de produto
        
        Args:
            id (int): ID do produto a buscar
        
        Returns:
            Produto: Dados completos do produto
        """
        return self.repository.buscar_por_id(id)