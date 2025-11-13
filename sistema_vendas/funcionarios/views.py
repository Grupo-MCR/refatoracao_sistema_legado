from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.middleware import csrf

# Create your views here.
def CadastrarFuncionario(request):
    if request.method == 'GET':
        csrf.get_token(request)
        template = loader.get_template('cadastrarFuncionario.html')
        return HttpResponse(template.render())
    else:
        return HttpResponseBadRequest("método de requet inválido :c")