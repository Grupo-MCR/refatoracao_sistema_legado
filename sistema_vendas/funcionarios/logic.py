from django.core import serializers
from .models import Funcionario

def buscarFuncionario(id: int):
    funcionario = Funcionario.objects.filter(id=id).values();
    print(funcionario[0]);
    return funcionario[0];

def buscarFuncionários():
    funcionariosList = []
    funcionarios = Funcionario.objects.all().values()
    for funcionario in funcionarios:
        funcionariosList.append(funcionario)
    return funcionariosList
