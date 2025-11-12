from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .logic import ClienteLogic


def consulta_cliente(request):
    """
    Renderiza a página de consulta de clientes
    """
    return render(request, 'consulta_cliente.html')


@require_http_methods(["GET"])
def listar_clientes(request):
    """
    Endpoint para listar todos os clientes (com busca opcional)
    GET /clientes/api/listar/
    """
    try:
        search = request.GET.get('search', '')
        clientes = ClienteLogic.listar_clientes(search)
        
        return JsonResponse({
            'success': True,
            'clientes': clientes
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def obter_cliente(request, cliente_id):
    """
    Endpoint para obter um cliente específico
    GET /clientes/api/obter/<id>/
    """
    try:
        cliente = ClienteLogic.obter_cliente(cliente_id)
        
        if cliente:
            return JsonResponse({
                'success': True,
                'cliente': cliente
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Cliente não encontrado'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def deletar_cliente(request, cliente_id):
    """
    Endpoint para deletar um cliente
    DELETE /clientes/api/deletar/<id>/
    """
    try:
        success = ClienteLogic.deletar_cliente(cliente_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Cliente deletado com sucesso'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Cliente não encontrado'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def criar_cliente(request):
    """
    Endpoint para criar um novo cliente
    POST /clientes/api/criar/
    """
    try:
        dados = json.loads(request.body)
        
        # Validações básicas
        if not dados.get('nome'):
            return JsonResponse({
                'success': False,
                'error': 'Nome é obrigatório'
            }, status=400)
        
        if not dados.get('cpf'):
            return JsonResponse({
                'success': False,
                'error': 'CPF é obrigatório'
            }, status=400)
        
        # Validar CPF
        if not ClienteLogic.validar_cpf(dados['cpf']):
            return JsonResponse({
                'success': False,
                'error': 'CPF inválido'
            }, status=400)
        
        cliente = ClienteLogic.criar_cliente(dados)
        
        return JsonResponse({
            'success': True,
            'cliente': cliente,
            'message': 'Cliente criado com sucesso'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def atualizar_cliente(request, cliente_id):
    """
    Endpoint para atualizar um cliente
    PUT /clientes/api/atualizar/<id>/
    """
    try:
        dados = json.loads(request.body)
        
        # Validar CPF se fornecido
        if dados.get('cpf') and not ClienteLogic.validar_cpf(dados['cpf']):
            return JsonResponse({
                'success': False,
                'error': 'CPF inválido'
            }, status=400)
        
        cliente = ClienteLogic.atualizar_cliente(cliente_id, dados)
        
        if cliente:
            return JsonResponse({
                'success': True,
                'cliente': cliente,
                'message': 'Cliente atualizado com sucesso'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Cliente não encontrado'
            }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)