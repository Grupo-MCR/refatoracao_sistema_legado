from .models import Funcionario

def buscarFuncionario(id: int):
    funcionario = Funcionario.objects.filter(id=id).values()
    print(funcionario[0])
    return funcionario[0]

def salvarFuncionario(funcionario: dict[str:any]):
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

        newFuncionario.save();

        return "funcionário salvo com sucesso"
        
    except Exception as a:
        print('algum problema aconteceu')
        print(a)
        raise a
    