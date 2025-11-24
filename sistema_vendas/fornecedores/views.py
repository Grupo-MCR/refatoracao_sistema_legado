from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.middleware import csrf
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .fornecedorService import FornecedorService
from .compraService import CompraService
from .models import Fornecedor
import json

# Cadastro de fornecedor (já existente)
def cadastrar_fornecedor(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('cadastrarFornecedor.html')
        return HttpResponse(template.render({}, request))
    
    elif request.method == 'POST':
        try:
            # Captura os dados do formulário
            dados = {
                'nome': request.POST.get('nome'),
                'cnpj': request.POST.get('cnpj'),
                'email': request.POST.get('email'),
                'telefone': request.POST.get('telefone'),
                'celular': request.POST.get('celular'),
                'cep': request.POST.get('cep'),
                'endereco': request.POST.get('endereco'),
                'numero': request.POST.get('numero'),
                'complemento': request.POST.get('complemento'),
                'bairro': request.POST.get('bairro'),
                'cidade': request.POST.get('cidade'),
                'estado': request.POST.get('estado'),
            }
            
            # Chama o service para cadastrar
            sucesso, mensagem, fornecedor = FornecedorService.cadastrar_fornecedor(dados)
            
            if sucesso:
                messages.success(request, mensagem)
                return redirect('consultaFornecedor')
            else:
                messages.error(request, mensagem)
                template = loader.get_template('cadastrarFornecedor.html')
                return HttpResponse(template.render({'dados': dados}, request))
                
        except Exception as e:
            messages.error(request, f"Erro ao processar requisição: {str(e)}")
            template = loader.get_template('cadastrarFornecedor.html')
            return HttpResponse(template.render({}, request))
    
    else:
        return HttpResponseBadRequest("Método de request inválido")

# Tela inicial - listagem de fornecedores
def consulta_fornecedor(request):
    """
    View para listar todos os fornecedores
    """
    if request.method == 'GET':
        csrf.get_token(request)
        
        # Busca todos os fornecedores
        fornecedores = FornecedorService.listar_fornecedores()
        
        template = loader.get_template('consultaFornecedor.html')
        contexto = {
            'fornecedores': fornecedores
        }
        return HttpResponse(template.render(contexto, request))
    else:
        return HttpResponseBadRequest("Método de request inválido")

# Tela de edição de fornecedor
def editar_fornecedor(request, fornecedor_id):
    """
    View para editar um fornecedor existente
    GET: Exibe o formulário preenchido
    POST: Processa a edição
    """
    if request.method == 'GET':
        csrf.get_token(request)
        
        # Busca o fornecedor
        fornecedor = FornecedorService.buscar_fornecedor(fornecedor_id)
        
        if not fornecedor:
            messages.error(request, "Fornecedor não encontrado")
            return redirect('consultaFornecedor')
        
        template = loader.get_template('editarFornecedor.html')
        contexto = {
            'id':fornecedor_id,
            'nome':fornecedor['nome'],
            'cnpj':fornecedor['cnpj'],
            'email':fornecedor['email'],
            'telefone':fornecedor['telefone'],
            'celular':fornecedor['celular'],
            'endereco':fornecedor['endereco'],
            'numero':fornecedor['numero'],
            'complemento':fornecedor['complemento'],
            'bairro':fornecedor['bairro'],
            'cep':fornecedor['cep'],
            'cidade':fornecedor['cidade'],
            'estado':fornecedor['estado'],
            }
        return HttpResponse(template.render(contexto, request))
    
    elif request.method == 'POST':
        try:
            # Captura os dados do formulário
            dados = {
                'nome': request.POST.get('nome'),
                'cnpj': request.POST.get('cnpj'),
                'email': request.POST.get('email'),
                'telefone': request.POST.get('telefone'),
                'celular': request.POST.get('celular'),
                'cep': request.POST.get('cep'),
                'endereco': request.POST.get('endereco'),
                'numero': request.POST.get('numero'),
                'complemento': request.POST.get('complemento'),
                'bairro': request.POST.get('bairro'),
                'cidade': request.POST.get('cidade'),
                'estado': request.POST.get('estado'),
            }
            
            # Chama o service para editar
            sucesso, mensagem, fornecedor = FornecedorService.editar_fornecedor(fornecedor_id, dados)
            
            if sucesso:
                messages.success(request, mensagem)
                return redirect('consultaFornecedor')
            else:
                messages.error(request, mensagem)
                fornecedor = FornecedorService.buscar_fornecedor(fornecedor_id)
                template = loader.get_template('editarFornecedor.html')
                return HttpResponse(template.render({'fornecedor': fornecedor}, request))
                
        except Exception as e:
            messages.error(request, f"Erro ao processar requisição: {str(e)}")
            fornecedor = FornecedorService.buscar_fornecedor(fornecedor_id)
            template = loader.get_template('editarFornecedor.html')
            return HttpResponse(template.render({'fornecedor': fornecedor}, request))
    
    else:
        return HttpResponseBadRequest("Método de request inválido")


# API para excluir fornecedor (opcional)
def excluir_fornecedor(request, fornecedor_id):
    """
    View para excluir um fornecedor
    """
    if request.method == 'POST':
        sucesso, mensagem = FornecedorService.excluir_fornecedor(fornecedor_id)
        
        if sucesso:
            messages.success(request, mensagem)
        else:
            messages.error(request, mensagem)
        
        return redirect('consultaFornecedor')
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
