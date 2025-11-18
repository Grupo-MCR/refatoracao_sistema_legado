from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.middleware import csrf
from .logic import buscarFuncionario

# Create your views here.
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
