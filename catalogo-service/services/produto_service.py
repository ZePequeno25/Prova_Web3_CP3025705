from repositories.produto_repository import ProdutoRepository
from models.produto import Produto
from dtos.produto_dto import ProdutoCreate

class ProdutoService:
    def __init__(self, repository: ProdutoRepository):
        self.repository = repository

    def criar_produto(self, dto: ProdutoCreate) -> Produto:
        produto = Produto(
            nome=dto.nome,
            descricao=dto.descricao,
            preco=dto.preco
        )
        return self.repository.criar(produto)

    def listar_produtos(self):
        return self.repository.listar()

    def buscar_por_id(self, id: int):
        return self.repository.buscar_por_id(id)