from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.middleware import csrf
from .logic import buscarFuncionario, salvarFuncionario, editarFuncionario

# Create your views here.
def ConsultarFuncionarios(request):
    if request.method == 'GET':
        template = loader.get_template('consultarFuncionarios.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("métdod de request inválido :c")

def CadastrarFuncionario(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('cadastrarFuncionario.html')
        return HttpResponse(template.render())
    elif request.method == "POST":
        try:
            body = request.POST
            message = salvarFuncionario(body)
            return HttpResponseRedirect('/funcionarios/cadastrar', False, message)
        except Exception:
            return HttpResponseBadRequest("campos obrigatórios não preenchidos ou informações inválidas")
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
            'complemento':funcionario['complemento'],
            'bairro':funcionario['bairro'],
            'cep':funcionario['cep'],
            'cidade':funcionario['cidade'],
            'estado':funcionario['estado'],
            }));
    elif request.method == 'POST':
        try:
            body = request.POST
            message = editarFuncionario(body, id)
            return HttpResponseRedirect('/funcionarios/cadastrar', False, message)
        except Exception:
            return HttpResponseBadRequest("campos obrigatórios não preenchidos ou informações inválidas")
    else:
        return HttpResponseBadRequest("método de request inválido :c")
