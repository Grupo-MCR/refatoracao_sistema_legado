from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest
from django.middleware import csrf

# Cadastro de fornecedor (já existente)
def CadastrarFuncionario(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('cadastrarFornecedor.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de request inválido :c")


# Tela inicial - listagem de fornecedores
def home_fornecedor(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('homeFornecedor.html')
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
