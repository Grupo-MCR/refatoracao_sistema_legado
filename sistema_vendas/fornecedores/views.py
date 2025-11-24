from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.middleware import csrf
from django.contrib import messages
from .fornecedorService import FornecedorService
import json


# Cadastro de fornecedor
def cadastrar_fornecedor(request):
    """
    View para cadastrar um novo fornecedor
    GET: Exibe o formulário
    POST: Processa o cadastro
    """
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
        return HttpResponseBadRequest("Método de request inválido")