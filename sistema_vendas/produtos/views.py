from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Count
from datetime import datetime
import json
import traceback
from .logic import ProdutoLogic


def consulta_produto(request):
    """
    Renderiza a página de consulta de produtos
    """
    return render(request, 'consulta_produto.html')

def cadastro_produto(request):
    """
    Renderiza a página de cadastro/edição de produtos
    """
    return render(request, 'cadastro_edicao_produto.html')

def relatorio_produtos(request):
    """
    Renderiza a página de relatório de produtos mais vendidos
    """
    return render(request, 'relatorio_produtos.html')

@require_http_methods(["GET"])
def listar_produtos(request):
    """
    Endpoint para listar todos os produtos (com busca opcional)
    GET /produtos/api/listar/
    """
    try:
        search = request.GET.get('search', '')
        produtos = ProdutoLogic.listar_produtos(search)
        
        return JsonResponse({
            'success': True,
            'produtos': produtos
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def obter_produto(request, produto_id):
    """
    Endpoint para obter um produto específico
    GET /produtos/api/obter/<id>/
    """
    try:
        produto = ProdutoLogic.obter_produto(produto_id)
        
        if produto:
            return JsonResponse({
                'success': True,
                'produto': produto
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Produto não encontrado'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def criar_produto(request):
    """
    Endpoint para criar um novo produto
    POST /produtos/api/criar/
    """
    try:
        data = json.loads(request.body)
        
        produto = ProdutoLogic.criar_produto(
            descricao=data.get('descricao'),
            preco=data.get('preco'),
            qtd_estoque=data.get('qtd_estoque'),
            fornecedor_id=data.get('fornecedor')
        )
        
        return JsonResponse({
            'success': True,
            'produto': produto,
            'message': 'Produto criado com sucesso'
        })
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def atualizar_produto(request, produto_id):
    """
    Endpoint para atualizar um produto existente
    PUT /produtos/api/atualizar/<id>/
    """
    try:
        data = json.loads(request.body)
        
        produto = ProdutoLogic.atualizar_produto(
            produto_id=produto_id,
            descricao=data.get('descricao'),
            preco=data.get('preco'),
            qtd_estoque=data.get('qtd_estoque'),
            fornecedor_id=data.get('fornecedor')
        )
        
        if produto:
            return JsonResponse({
                'success': True,
                'produto': produto,
                'message': 'Produto atualizado com sucesso'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Produto não encontrado'
            }, status=404)
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def deletar_produto(request, produto_id):
    """
    Endpoint para deletar um produto
    DELETE /produtos/api/deletar/<id>/
    """
    try:
        success = ProdutoLogic.deletar_produto(produto_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Produto deletado com sucesso'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Produto não encontrado'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def listar_fornecedores(request):
    """
    Endpoint para listar todos os fornecedores
    GET /produtos/api/fornecedores/
    """
    try:
        fornecedores = ProdutoLogic.listar_fornecedores()
        
        return JsonResponse({
            'success': True,
            'fornecedores': fornecedores
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================
# NOVA VIEW PARA RELATÓRIO DE PRODUTOS
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def relatorio_produtos_vendidos(request):
    """
    Gera relatório de produtos mais vendidos em um período
    POST /produtos/api/relatorio/
    Espera JSON: {"dataInicio": "DD/MM/YYYY", "dataFinal": "DD/MM/YYYY"}
    Retorna: lista dos produtos mais vendidos
    """
    try:
        data = json.loads(request.body)
        data_inicio = data.get('dataInicio')
        data_final = data.get('dataFinal')
        
        print(f"[DEBUG] Gerando relatório - Período: {data_inicio} até {data_final}")
        
        # Converter datas de DD/MM/YYYY para objeto datetime
        data_inicio_obj = datetime.strptime(data_inicio, '%d/%m/%Y')
        data_final_obj = datetime.strptime(data_final, '%d/%m/%Y')
        
        # Importar os modelos necessários
        from vendas.models import ItemVenda
        from .models import Produto
        
        # Buscar os produtos mais vendidos no período
        # Agrupa por produto e soma as quantidades vendidas
        produtos_vendidos = ItemVenda.objects.filter(
            venda_id__data_venda__date__gte=data_inicio_obj.date(),
            venda_id__data_venda__date__lte=data_final_obj.date()
        ).values(
            'produto_id',
            'produto_id__id',
            'produto_id__descricao',
            'produto_id__preco'
        ).annotate(
            quantidade_vendida=Sum('quantidade'),
            valor_total=Sum('subTotal')
        ).order_by('-quantidade_vendida')[:10]  # Top 10 produtos
        
        print(f"[DEBUG] Produtos encontrados: {produtos_vendidos.count()}")
        
        # Formatar dados para retorno
        produtos_list = []
        for item in produtos_vendidos:
            produtos_list.append({
                'id': item['produto_id__id'],
                'descricao': item['produto_id__descricao'],
                'quantidade_vendida': item['quantidade_vendida'],
                'valor_total': f"R$ {float(item['valor_total']):.2f}".replace('.', ','),
                'preco_unitario': f"R$ {float(item['produto_id__preco']):.2f}".replace('.', ',')
            })
        
        return JsonResponse({
            'success': True,
            'produtos': produtos_list,
            'periodo': {
                'inicio': data_inicio,
                'fim': data_final
            }
        })
        
    except ValueError as e:
        print(f"[ERRO] Data inválida: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Data inválida. Use o formato DD/MM/YYYY'
        }, status=400)
        
    except Exception as e:
        print(f"[ERRO] Erro ao gerar relatório: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Erro no servidor: {str(e)}'
        }, status=500)