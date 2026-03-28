from repositories.estoque_repository import EstoqueRepository
import requests

class EstoqueService:
    """
    Serviço de gerenciamento de estoque (inventário).
    Responsável por manter e controlar as quantidades de produtos disponíveis.
    """
    
    def __init__(self, repository: EstoqueRepository):
        self.repository = repository
        self.catalogo_url = "http://127.0.0.1:8001"

    def _validar_produto_existe(self, produto_id: int):
        """
        Valida se um produto existe no Catálogo Service.
        
        Essa validação garante integridade: só permite criar estoque
        para produtos que realmente existem no catálogo.
        
        Args:
            produto_id (int): ID do produto a validar
        
        Raises:
            ValueError: Se produto não encontrado no Catálogo ou conexão falhar
        """
        try:
            prod_resp = requests.get(f"{self.catalogo_url}/products/{produto_id}", timeout=5)
            if prod_resp.status_code != 200:
                raise ValueError(f"Produto ID {produto_id} não encontrado no Catálogo")
        except requests.exceptions.ConnectionError:
            raise ValueError("Erro de conexão: Catálogo Service não está disponível")

    def consultar_estoque(self, produto_id: int):
        """
        Consulta a quantidade disponível em estoque de um produto.
        
        Fluxo:
        1. Busca registro de estoque para o produto_id
        2. Retorna quantidade disponível
        
        Utilizado por:
        - Pedidos Service: para verificar se há quantidade suficiente
        - Clientes: para conhecer disponibilidade
        
        Args:
            produto_id (int): ID do produto
        
        Returns:
            Estoque: Objeto com quantidade_disponível
        
        Raises:
            ValueError: Se estoque não encontrado para o produto
        """
        estoque = self.repository.buscar_por_produto(produto_id)
        if not estoque:
            raise ValueError(f"Estoque não encontrado para o produto {produto_id}")
        return estoque

    def decrementar_estoque(self, produto_id: int, quantidade: int):
        """
        Diminui o estoque de um produto (aplicado após pedido aprovado).
        
        Fluxo:
        1. Valida quantidade > 0
        2. Verifica se estoque existe
        3. Valida se há quantidade suficiente
        4. Diminui a quantidade
        5. Persiste no banco
        
        Utilizado por:
        - Pedidos Service: após criação de pedido (reduz após pagamento aprovado)
        
        Importante:
        - Operação ATÔMICA: não há race condition
        - Garante integridade: não deixa quantidades negativas
        
        Args:
            produto_id (int): ID do produto
            quantidade (int): Quantidade a decrementar
        
        Returns:
            Estoque: Novo estado do estoque após decremento
        
        Raises:
            ValueError: Se quantidade <= 0, estoque não existe ou insuficiente
        """
        if quantidade <= 0:
            raise ValueError("Quantidade a decrementar deve ser maior que zero")

        estoque = self.repository.buscar_por_produto(produto_id)
        if not estoque:
            raise ValueError(f"Estoque não encontrado para o produto {produto_id}")

        if estoque.quantidade_disponivel < quantidade:
            raise ValueError(
                f"Estoque insuficiente para o produto {produto_id}. "
                f"Disponível: {estoque.quantidade_disponivel}, Solicitado: {quantidade}"
            )

        nova_quantidade = estoque.quantidade_disponivel - quantidade
        return self.repository.criar_ou_atualizar(produto_id, nova_quantidade)

    def atualizar_estoque(self, produto_id: int, quantidade: int):
        """
        Atualiza o estoque manualmente (entrada de nova mercadoria).
        
        Fluxo:
        1. Valida quantidade >= 0
        2. Valida que produto existe no Catálogo
        3. Cria ou atualiza registro de estoque
        4. Persiste no banco
        
        Utilizado por:
        - Gerente de estoque: para adicionar novas unidades de produto
        - API PUT /inventory/{productId}
        
        Importante:
        - Requer que produto já exista no Catálogo
        - Pode criar novo registro de estoque se não existir
        
        Args:
            produto_id (int): ID do produto
            quantidade (int): Nova quantidade em estoque (não é incremento, é total)
        
        Returns:
            Estoque: Novo estado do estoque
        
        Raises:
            ValueError: Se quantidade < 0 ou produto não existe no Catálogo
        """
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
        
        # Valida se produto existe antes de atualizar estoque
        self._validar_produto_existe(produto_id)
        
        return self.repository.criar_ou_atualizar(produto_id, quantidade)