from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, HttpResponseServerError ,JsonResponse
from django.middleware import csrf
from .logic import buscarFuncionario, buscarFuncionários, apagarFuncionario

# Create your views here.
def ConsultarFuncionarios(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('consultarFuncionarios.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de requisição inválido :c")

def ListarFuncionarios(request):
    if request.method == 'GET':
        responseData = buscarFuncionários()
        return JsonResponse(responseData, safe=False)
    else:
        return HttpResponseBadRequest("método de requisição inválido :c")

def CadastrarFuncionario(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('cadastrarFuncionario.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de requet inválido :c")
    
def EditarFuncionario(request, id):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('editarFuncionario.html')
        funcionario = buscarFuncionario(id);
        return HttpResponse(template.render({
            'nome':funcionario['nome'],
            'cpf':funcionario['cpf'],
            'email':funcionario['email'],
            'rg':funcionario['rg'],
            'senha':funcionario['senha'],
            'telefone':funcionario['telefone'],
            'nvacesso':funcionario['nivel_acesso'],
            'celular':funcionario['celular'],
            'cargo':funcionario['cargo'],
            'rua':funcionario['rua'],
            'numero':funcionario['numero'],
            'bairro':funcionario['bairro'],
            'cep':funcionario['cep'],
            'cidade':funcionario['cidade'],
            'estado':funcionario['estado'],
            }));
    else:
        return HttpResponseBadRequest("método de request inválido :c")

def DeletarFuncionario(request, id):
    if request.method == 'DELETE':
        try:
            message = apagarFuncionario(id);
            return HttpResponseRedirect("/funcionarios/consultar", True, message)
        except Exception:
            return HttpResponseServerError("erro ao apagar funcionário :P")
    else:
        return HttpResponseBadRequest("método de request inválido :c")
