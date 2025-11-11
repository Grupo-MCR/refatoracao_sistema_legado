from .models import Produto
from fornecedores.models import Fornecedor
from django.db.models import Q


class ProdutoLogic:
    """
    Classe com a lógica de negócio para Produtos
    """
    
    @staticmethod
    def listar_produtos(search=''):
        """
        Lista todos os produtos com filtro de busca opcional
        """
        if search:
            produtos = Produto.objects.filter(
                Q(descricao__icontains=search) | 
                Q(fornecedor__nome__icontains=search)
            ).select_related('fornecedor')
        else:
            produtos = Produto.objects.all().select_related('fornecedor')
        
        # Converter para lista de dicionários
        produtos_list = []
        for produto in produtos:
            produtos_list.append({
                'id': produto.id,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'qtd_estoque': produto.qtd_estoque,
                'fornecedor': {
                    'id': produto.fornecedor.id,
                    'nome': produto.fornecedor.nome,
                    'cnpj': produto.fornecedor.cnpj
                }
            })
        
        return produtos_list
    
    @staticmethod
    def obter_produto(produto_id):
        """
        Obtém um produto específico por ID
        """
        try:
            produto = Produto.objects.select_related('fornecedor').get(id=produto_id)
            return {
                'id': produto.id,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'qtd_estoque': produto.qtd_estoque,
                'fornecedor': {
                    'id': produto.fornecedor.id,
                    'nome': produto.fornecedor.nome,
                    'cnpj': produto.fornecedor.cnpj
                }
            }
        except Produto.DoesNotExist:
            return None
    
    @staticmethod
    def criar_produto(descricao, preco, qtd_estoque, fornecedor_id):
        """
        Cria um novo produto
        """
        try:
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            produto = Produto.objects.create(
                descricao=descricao,
                preco=preco,
                qtd_estoque=qtd_estoque,
                fornecedor=fornecedor
            )
            return {
                'id': produto.id,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'qtd_estoque': produto.qtd_estoque,
                'fornecedor': {
                    'id': produto.fornecedor.id,
                    'nome': produto.fornecedor.nome,
                    'cnpj': produto.fornecedor.cnpj
                }
            }
        except Fornecedor.DoesNotExist:
            raise ValueError('Fornecedor não encontrado')
    
    @staticmethod
    def atualizar_produto(produto_id, descricao, preco, qtd_estoque, fornecedor_id):
        """
        Atualiza um produto existente
        """
        try:
            produto = Produto.objects.get(id=produto_id)
            fornecedor = Fornecedor.objects.get(id=fornecedor_id)
            
            produto.descricao = descricao
            produto.preco = preco
            produto.qtd_estoque = qtd_estoque
            produto.fornecedor = fornecedor
            produto.save()
            
            return {
                'id': produto.id,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'qtd_estoque': produto.qtd_estoque,
                'fornecedor': {
                    'id': produto.fornecedor.id,
                    'nome': produto.fornecedor.nome,
                    'cnpj': produto.fornecedor.cnpj
                }
            }
        except Produto.DoesNotExist:
            return None
        except Fornecedor.DoesNotExist:
            raise ValueError('Fornecedor não encontrado')
    
    @staticmethod
    def deletar_produto(produto_id):
        """
        Deleta um produto
        """
        try:
            produto = Produto.objects.get(id=produto_id)
            produto.delete()
            return True
        except Produto.DoesNotExist:
            return False
    
    @staticmethod
    def listar_fornecedores():
        """
        Lista todos os fornecedores
        """
        fornecedores = Fornecedor.objects.all()
        
        fornecedores_list = []
        for fornecedor in fornecedores:
            fornecedores_list.append({
                'id': fornecedor.id,
                'nome': fornecedor.nome,
                'cnpj': fornecedor.cnpj,
                'email': fornecedor.email,
                'telefone': fornecedor.telefone
            })
        
        return fornecedores_list