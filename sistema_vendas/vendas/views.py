from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.
def Venda(request):
 template = loader.get_template('ponto_vendas.html')
 return HttpResponse(template.render())

def Pagamento(request):
 template = loader.get_template('pagamento.html')
 return HttpResponse(template.render())