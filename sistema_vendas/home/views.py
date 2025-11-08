from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.template import loader
from django.middleware import csrf
from .logic import validarLogin

# Create your views here.
def Login(request):
    if request.method == "GET":
        csrf.get_token(request)
        template = loader.get_template('login.html')
        return HttpResponse(template.render())
    elif request.method == "POST":
        print(request)
        obj = request.POST
        fd = obj.dict()
        if validarLogin(fd):
            return HttpResponseRedirect('/login/')
        else:
            return HttpResponseBadRequest("credenciais inválidas")
    else: 
        return HttpResponse("Erro: método de request inválido lol")
