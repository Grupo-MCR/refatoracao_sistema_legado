from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .logic import ProdutoLogic


def consulta_produto(request):
    """
    Renderiza a página de consulta de produtos
    """
    return render(request, 'consulta_produto.html')


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