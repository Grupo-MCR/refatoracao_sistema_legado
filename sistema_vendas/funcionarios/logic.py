from .models import Funcionario

def buscarFuncionario(id: int):
    funcionario = Funcionario.objects.filter(id=id).values()
    return funcionario[0]

def salvarFuncionario(funcionario: dict[str:any]):
    print(funcionario['nome'])
    try :
        newFuncionario = Funcionario();
        newFuncionario.nome = funcionario['nome']
        newFuncionario.rg = funcionario['rg']
        newFuncionario.cpf = funcionario['cpf']
        newFuncionario.email = funcionario['email']
        newFuncionario.senha = funcionario['senha']
        newFuncionario.nivel_acesso = funcionario['nivelAcesso']
        newFuncionario.cargo = funcionario['cargo']
        newFuncionario.telefone = funcionario['telefone']
        newFuncionario.celular = funcionario['celular']
        newFuncionario.rua = funcionario['rua']
        newFuncionario.numero = funcionario['numero']
        newFuncionario.bairro = funcionario['bairro']
        newFuncionario.complemento = funcionario['complemento']
        newFuncionario.cidade = funcionario['cidade']
        newFuncionario.estado = funcionario['estado']
        newFuncionario.cep = funcionario['cep']

        newFuncionario.save()

        return "funcionário salvo com sucesso"
        
    except Exception as error:
        print('algum problema aconteceu')
        print(error)
        raise error
    
def editarFuncionario(funcionarioEdit: dict[str:any], id: int):
    try:
        funcionario = Funcionario.objects.filter(id=id)[0]

        funcionario.nome = funcionarioEdit['nome']
        funcionario.senha = funcionarioEdit['senha']
        funcionario.cargo = funcionarioEdit['cargo']
        funcionario.nivel_acesso = funcionarioEdit['nivelAcesso']
        funcionario.rg = funcionarioEdit['rg']
        funcionario.cpf = funcionarioEdit['cpf']
        funcionario.email = funcionarioEdit['email']
        funcionario.telefone = funcionarioEdit['telefone']
        funcionario.celular = funcionarioEdit['celular']
        funcionario.cep = funcionarioEdit['cep']
        funcionario.rua = funcionarioEdit['rua']
        funcionario.numero = funcionarioEdit['numero']
        funcionario.complemento = funcionarioEdit['complemento']
        funcionario.bairro = funcionarioEdit['bairro']
        funcionario.cidade = funcionarioEdit['cidade']
        funcionario.estado = funcionarioEdit['estado']

        funcionario.save()

        return "dados do funcionário atualizados com sucesso"
    
    except Exception as error:
        print("algum problema aconteceu")
        print(error)
        raise error
        