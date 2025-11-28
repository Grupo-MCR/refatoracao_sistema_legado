from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Compra, Fornecedor

from datetime import datetime
import json


class CompraService:
    """
    Serviço para gerenciar operações de compras de fornecedores
    """
    
    @staticmethod
    def gerar_numero_pedido():
        """
        Gera um número único para o pedido de compra
        Formato: COMP-YYYYMMDD-XXXX
        """
        hoje = timezone.now()
        data_str = hoje.strftime('%Y%m%d')
        
        # Busca o último pedido do dia
        ultimo_pedido = Compra.objects.filter(
            numero_pedido__startswith=f'COMP-{data_str}'
        ).order_by('-numero_pedido').first()
        
        if ultimo_pedido:
            # Extrai o número sequencial e incrementa
            ultimo_numero = int(ultimo_pedido.numero_pedido.split('-')[-1])
            proximo_numero = ultimo_numero + 1
        else:
            proximo_numero = 1
        
        return f'COMP-{data_str}-{proximo_numero:04d}'
    
    @staticmethod
    def converter_data_br_para_datetime(data_str):
        """
        Converte data no formato brasileiro (dd/mm/yyyy) para datetime
        """
        try:
            data_obj = datetime.strptime(data_str, '%d/%m/%Y')
            return timezone.make_aware(data_obj)
        except ValueError:
            raise ValueError(f"Formato de data inválido: {data_str}. Use dd/mm/yyyy")
    
    @staticmethod
    @transaction.atomic
    def cadastrar_compra(dados, usuario=None):
        """
        Cadastra uma nova compra de fornecedor
        
        Args:
            dados (dict): Dicionário com os dados da compra
                - data_compra (str): Data da compra no formato dd/mm/yyyy
                - id_fornecedor (int): ID do fornecedor
                - status (str): Status da compra
                - observacoes (str, optional): Observações
                - itens (list): Lista de itens da compra
                    - id_produto (int): ID do produto
                    - quantidade (int): Quantidade
                    - preco_unitario (float): Preço unitário
            usuario (User, optional): Usuário que está criando a compra
        
        Returns:
            dict: Resultado da operação com sucesso e dados da compra
        """
        try:
            # Validações básicas
            if not dados.get('itens') or len(dados['itens']) == 0:
                return {
                    'success': False,
                    'error': 'É necessário adicionar pelo menos um item à compra'
                }
            
            # Busca o fornecedor
            from produtos.models import Produto
            try:
                fornecedor = Fornecedor.objects.get(id=dados['id_fornecedor'])
            except Fornecedor.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Fornecedor não encontrado'
                }
            
            # Converte a data
            data_compra = CompraService.converter_data_br_para_datetime(
                dados['data_compra']
            )
            
            # Gera número do pedido
            numero_pedido = CompraService.gerar_numero_pedido()
            
            # Calcula o valor total
            valor_total = Decimal('0.00')
            itens_validados = []
            
            for item in dados['itens']:
                try:
                    produto = Produto.objects.get(id=item['id_produto'])
                except Produto.DoesNotExist:
                    return {
                        'success': False,
                        'error': f'Produto com ID {item["id_produto"]} não encontrado'
                    }
                
                quantidade = int(item['quantidade'])
                preco_unitario = Decimal(str(item['preco_unitario']))
                
                if quantidade <= 0:
                    return {
                        'success': False,
                        'error': 'A quantidade deve ser maior que zero'
                    }
                
                if preco_unitario < 0:
                    return {
                        'success': False,
                        'error': 'O preço unitário não pode ser negativo'
                    }
                
                subtotal = preco_unitario * quantidade
                valor_total += subtotal
                
                itens_validados.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'preco_unitario': preco_unitario,
                    'subtotal': subtotal
                })
            
            # Cria a compra
            compra = Compra.objects.create(
                numero_pedido=numero_pedido,
                fornecedor=fornecedor,
                data_compra=data_compra,
                status=dados.get('status', 'pendente'),
                valor_total=valor_total,
                observacoes=dados.get('observacoes'),
                criado_por=usuario
            )
            
            # Cria os itens da compra
            
            from .models import ItemCompra
            for item in itens_validados:
                ItemCompra.objects.create(
                    compra=compra,
                    produto=item['produto'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco_unitario'],
                    subtotal=item['subtotal']
                )
            
            return {
                'success': True,
                'message': 'Compra cadastrada com sucesso',
                'compra': {
                    'id': compra.id,
                    'numero_pedido': compra.numero_pedido,
                    'fornecedor': fornecedor.nome,
                    'data_compra': compra.data_compra.strftime('%d/%m/%Y'),
                    'status': compra.status,
                    'valor_total': float(compra.valor_total),
                    'itens': [
                        {
                            'produto': item['produto'].descricao,
                            'quantidade': item['quantidade'],
                            'preco_unitario': float(item['preco_unitario']),
                            'subtotal': float(item['subtotal'])
                        }
                        for item in itens_validados
                    ]
                }
            }
            
        except ValueError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao cadastrar compra: {str(e)}'
            }
    
    @staticmethod
    def listar_compras(filtros=None):
        """
        Lista todas as compras com filtros opcionais (INCLUINDO OS ITENS)
        
        Args:
            filtros (dict, optional): Filtros para a consulta
                - fornecedor_id (int): ID do fornecedor
                - status (str): Status da compra
                - data_inicio (str): Data início no formato dd/mm/yyyy
                - data_fim (str): Data fim no formato dd/mm/yyyy
        
        Returns:
            dict: Lista de compras com seus itens
        """
        try:
            from .models import ItemCompra
            
            compras = Compra.objects.select_related('fornecedor', 'criado_por').prefetch_related('itens__produto').all()
            
            if filtros:
                if filtros.get('fornecedor_id'):
                    compras = compras.filter(fornecedor_id=filtros['fornecedor_id'])
                
                if filtros.get('status'):
                    compras = compras.filter(status=filtros['status'])
                
                if filtros.get('data_inicio'):
                    data_inicio = CompraService.converter_data_br_para_datetime(
                        filtros['data_inicio']
                    )
                    compras = compras.filter(data_compra__gte=data_inicio)
                
                if filtros.get('data_fim'):
                    data_fim = CompraService.converter_data_br_para_datetime(
                        filtros['data_fim']
                    )
                    compras = compras.filter(data_compra__lte=data_fim)
            
            return {
                'success': True,
                'compras': [
                    {
                        'id': compra.id,
                        'numero_pedido': compra.numero_pedido,
                        'fornecedor': compra.fornecedor.nome,
                        'data_compra': compra.data_compra.strftime('%d/%m/%Y'),
                        'status': compra.status,
                        'valor_total': float(compra.valor_total),
                        'criado_por': compra.criado_por.username if compra.criado_por else None,
                        # ADICIONADO: Incluir os itens da compra
                        'itens': [
                            {
                                'produto': item.produto.descricao,
                                'quantidade': item.quantidade,
                                'preco_unitario': float(item.preco_unitario),
                                'subtotal': float(item.subtotal)
                            }
                            for item in compra.itens.all()
                        ]
                    }
                    for compra in compras
                ]
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao listar compras: {str(e)}'
            }
    
    @staticmethod
    def buscar_compra_por_id(compra_id):
        """
        Busca uma compra específica pelo ID
        
        Args:
            compra_id (int): ID da compra
        
        Returns:
            dict: Dados da compra
        """
        try:
            compra = Compra.objects.select_related('fornecedor', 'criado_por').get(id=compra_id)
            
            return {
                'success': True,
                'compra': {
                    'id': compra.id,
                    'numero_pedido': compra.numero_pedido,
                    'fornecedor': {
                        'id': compra.fornecedor.id,
                        'nome': compra.fornecedor.nome
                    },
                    'data_compra': compra.data_compra.strftime('%d/%m/%Y'),
                    'status': compra.status,
                    'valor_total': float(compra.valor_total),
                    'valor_frete': float(compra.valor_frete),
                    'valor_desconto': float(compra.valor_desconto),
                    'observacoes': compra.observacoes,
                    'criado_por': compra.criado_por.username if compra.criado_por else None,
                    'criado_em': compra.criado_em.strftime('%d/%m/%Y %H:%M')
                }
            }
        except Compra.DoesNotExist:
            return {
                'success': False,
                'error': 'Compra não encontrada'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao buscar compra: {str(e)}'
            }
    
    @staticmethod
    @transaction.atomic
    def atualizar_status_compra(compra_id, novo_status):
        """
        Atualiza o status de uma compra
        
        Args:
            compra_id (int): ID da compra
            novo_status (str): Novo status
        
        Returns:
            dict: Resultado da operação
        """
        try:
            compra = Compra.objects.get(id=compra_id)
            
            status_validos = ['pendente', 'processando', 'concluida', 'cancelada']
            if novo_status not in status_validos:
                return {
                    'success': False,
                    'error': f'Status inválido. Valores aceitos: {", ".join(status_validos)}'
                }
            
            compra.status = novo_status
            compra.save()
            
            return {
                'success': True,
                'message': 'Status atualizado com sucesso',
                'compra': {
                    'id': compra.id,
                    'numero_pedido': compra.numero_pedido,
                    'status': compra.status
                }
            }
        except Compra.DoesNotExist:
            return {
                'success': False,
                'error': 'Compra não encontrada'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erro ao atualizar status: {str(e)}'
            }
