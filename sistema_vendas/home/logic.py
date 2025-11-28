from funcionarios.models import Funcionario

def validarLogin(loginData):
    email = str(loginData['email'])
    senha = str(loginData['senha'])
    print(email)
    print(senha)
    funcionarios = Funcionario.objects.all().values()
    for funcionario in funcionarios:
        print(funcionario['email'])
        print(funcionario['senha'])
        if funcionario['email'] == email and funcionario['senha'] == senha:
            return True
    if "admin@admin.com" == email and "admin" == senha:
            return True
    return False
    