from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .compraService import CompraService
from .models import Fornecedor

# Cadastro de fornecedor (já existente)
def cadastrar_fornecedor(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('cadastrarFornecedor.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de request inválido :c")

# Tela inicial - listagem de fornecedores
def consulta_fornecedor(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('consultaFornecedor.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de request inválido :c")

# Tela de edição de fornecedor
def editar_fornecedor(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('editarFornecedor.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de request inválido :c")

# Tela de compra de fornecedor
def compra_fornecedor(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('compraFornecedorInterface.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de request inválido :c")


# ==================== VIEWS DE API (JSON) ====================

@csrf_exempt
@require_http_methods(["POST"] )
def cadastrar_compra_api(request):
    """
    API para cadastrar uma nova compra de fornecedor
    
    Esperado no body (JSON):
    {
        "data_compra": "19/11/2025",
        "id_fornecedor": 1,
        "status": "pendente",
        "observacoes": "Texto opcional",
        "itens": [
            {
                "id_produto": 1,
                "quantidade": 10,
                "preco_unitario": 15.50
            }
        ]
    }
    """
    try:
        dados = json.loads(request.body)
        
        # Pega o usuário autenticado (se existir)
        usuario = request.user if request.user.is_authenticated else None
        
        # Chama o serviço para cadastrar a compra
        resultado = CompraService.cadastrar_compra(dados, usuario)
        
        if resultado['success']:
            return JsonResponse(resultado, status=201)
        else:
            return JsonResponse(resultado, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro interno: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"] )
def listar_compras_api(request):
    """
    API para listar compras com filtros opcionais
    
    Query params opcionais:
    - fornecedor_id: ID do fornecedor
    - status: Status da compra
    - data_inicio: Data início (dd/mm/yyyy)
    - data_fim: Data fim (dd/mm/yyyy)
    """
    try:
        filtros = {
            'fornecedor_id': request.GET.get('fornecedor_id'),
            'status': request.GET.get('status'),
            'data_inicio': request.GET.get('data_inicio'),
            'data_fim': request.GET.get('data_fim')
        }
        
        # Remove filtros vazios
        filtros = {k: v for k, v in filtros.items() if v}
        
        resultado = CompraService.listar_compras(filtros)
        return JsonResponse(resultado)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao listar compras: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"] )
def buscar_compra_api(request, compra_id):
    """
    API para buscar uma compra específica pelo ID
    """
    try:
        resultado = CompraService.buscar_compra_por_id(compra_id)
        
        if resultado['success']:
            return JsonResponse(resultado)
        else:
            return JsonResponse(resultado, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao buscar compra: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["PUT", "PATCH"] )
def atualizar_status_compra_api(request, compra_id):
    """
    API para atualizar o status de uma compra
    
    Esperado no body (JSON):
    {
        "status": "concluida"
    }
    """
    try:
        dados = json.loads(request.body)
        novo_status = dados.get('status')
        
        if not novo_status:
            return JsonResponse({
                'success': False,
                'error': 'O campo "status" é obrigatório'
            }, status=400)
        
        resultado = CompraService.atualizar_status_compra(compra_id, novo_status)
        
        if resultado['success']:
            return JsonResponse(resultado)
        else:
            return JsonResponse(resultado, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao atualizar status: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"] )
def listar_fornecedores_api(request):
    """
    API para listar todos os fornecedores
    """
    try:
        fornecedores = Fornecedor.objects.all()
        
        return JsonResponse({
            'success': True,
            'fornecedores': [
                {
                    'id': f.id,
                    'nome': f.nome,
                    'cnpj': f.cnpj,
                    'email': f.email,
                    'telefone': f.telefone,
                    'celular': f.celular,
                    'cidade': f.cidade,
                    'estado': f.estado
                }
                for f in fornecedores
            ]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao listar fornecedores: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"] )
def listar_produtos_api(request):
    """
    API para listar todos os produtos
    """
    try:
        from produtos.models import Produto
        produtos = Produto.objects.all()
        
        return JsonResponse({
            'success': True,
            'produtos': [
                {
                    'id': p.id,
                    'descricao': p.descricao,
                    'preco': float(p.preco),
                    'estoque': p.qtd_estoque
                }
                for p in produtos
            ]
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao listar produtos: {str(e)}'
        }, status=500)
