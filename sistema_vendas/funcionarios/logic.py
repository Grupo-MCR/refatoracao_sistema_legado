from .models import Funcionario

def buscarFuncionario(id: int):
    funcionario = Funcionario.objects.filter(id=id).values();
    print(funcionario[0]);
    return funcionario[0]; 
