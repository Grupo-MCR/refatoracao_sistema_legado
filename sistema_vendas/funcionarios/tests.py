from django.test import TestCase, Client
from .models import Funcionario
from .logic import buscarFuncionario, salvarFuncionario, editarFuncionario

# Create your tests here.
class FuncionarioServiceTestCase(TestCase):
    funcionarioMap: dict[str:any] = {}

    def setUp(self):
        Funcionario.objects.create(id=1225, 
                                   nome="testUser", 
                                   email="test@test.com", 
                                   senha="test", 
                                   cargo="teste", 
                                   nivel_acesso=1, 
                                   rg="1.111.111",  
                                   cpf="111.111.111-11", 
                                   telefone="45 9999-9999", 
                                   celular="99 4545-4545", 
                                   rua="rua", 
                                   numero=1111, 
                                   complemento="kasa", 
                                   bairro="bairro", 
                                   cidade="cidade", 
                                   estado="PR", 
                                   cep=11111111)
        
        self.funcionarioMap['id'] = 2512
        self.funcionarioMap['nome'] = "testUserMap"
        self.funcionarioMap['email'] = "test2@test.com"
        self.funcionarioMap['senha'] = "test"
        self.funcionarioMap['cargo'] = "test"
        self.funcionarioMap['nivelAcesso'] = 1
        self.funcionarioMap['rg'] = "2.222.222"
        self.funcionarioMap['cpf'] = "222.222.222-22"
        self.funcionarioMap['telefone'] = "11 2222-2222"
        self.funcionarioMap['celular'] = "22 1111-1111"
        self.funcionarioMap['rua'] = "rua2"
        self.funcionarioMap['numero'] = 2222
        self.funcionarioMap['complemento'] = "home"
        self.funcionarioMap['bairro'] = "bairro2"
        self.funcionarioMap['cidade'] = "cidade2"
        self.funcionarioMap['estado'] = "PR"
        self.funcionarioMap['cep'] = 22222222

    def testBuscarFuncionario(self):
        testUser = Funcionario.objects.filter(id=1225).values()[0]
        self.assertEqual(buscarFuncionario(1225), testUser)

    def testSalvarFuncionario(self):
        self.assertEqual(salvarFuncionario(self.funcionarioMap), "funcionário salvo com sucesso")

    def testEditarFuncionario(self):
        self.assertEqual(editarFuncionario(self.funcionarioMap, 1225), "dados do funcionário atualizados com sucesso")
    
    def testApagarFuncionario(self):
        testUser1 = Funcionario.objects.get(id=1225)
        result = testUser1.delete()
        self.assertEqual(result, (1, {'funcionarios.Funcionario': 1}))

class FuncionariosPathsTestCase(TestCase):
    mock = Client()
    funcionarioMap: dict[str:any] = {}
    requestPageCadastro: any
    requestPageEditar: any
    requestPageConsulta: any
    requestCadastro: any
    requestEdicao: any

    def setUp(self):
        Funcionario.objects.create(id=1225, 
                                   nome="testUser", 
                                   email="test@test.com", 
                                   senha="test", 
                                   cargo="teste", 
                                   nivel_acesso=1, 
                                   rg="1.111.111",  
                                   cpf="111.111.111-11", 
                                   telefone="45 9999-9999", 
                                   celular="99 4545-4545", 
                                   rua="rua", 
                                   numero=1111, 
                                   complemento="kasa", 
                                   bairro="bairro", 
                                   cidade="cidade", 
                                   estado="PR", 
                                   cep=11111111).save()
        
        self.funcionarioMap['id'] = 2512
        self.funcionarioMap['nome'] = "testUserMap"
        self.funcionarioMap['email'] = "test2@test.com"
        self.funcionarioMap['senha'] = "test"
        self.funcionarioMap['cargo'] = "test"
        self.funcionarioMap['nivelAcesso'] = 1
        self.funcionarioMap['rg'] = "2.222.222"
        self.funcionarioMap['cpf'] = "222.222.222-22"
        self.funcionarioMap['telefone'] = "11 2222-2222"
        self.funcionarioMap['celular'] = "22 1111-1111"
        self.funcionarioMap['rua'] = "rua2"
        self.funcionarioMap['numero'] = 2222
        self.funcionarioMap['complemento'] = "home"
        self.funcionarioMap['bairro'] = "bairro2"
        self.funcionarioMap['cidade'] = "cidade2"
        self.funcionarioMap['estado'] = "PR"
        self.funcionarioMap['cep'] = 22222222

        self.requestPageCadastro = self.mock.get("/funcionarios/cadastrar/")
        self.requestPageEditar = self.mock.get("/funcionarios/editar/id=1225")
        self.requestPageConsulta = self.mock.get("/funcionarios/consultar/")

        self.requestCadastro = self.mock.post("/funcionarios/cadastrar/", self.funcionarioMap)
        self.funcionarioMap['email'] = "test3@test.com"
        self.funcionarioMap['telefone'] = "67 6767-6767"
        self.requestEdicao = self.mock.post("/funcionarios/editar/id=1225", self.funcionarioMap)

    def testCadastroGet(self):
        """ teste de método get da página de cadastro de funcionário """
        self.assertEqual(self.requestPageCadastro.status_code, 200)

    def testEditarGet(self):
        """ teste de método get da página de edição de funcionário """
        self.assertEqual(self.requestPageEditar.status_code, 200)
    
    def testConsultaGet(self):
        """ teste de método get da página de consulta de funcionário """
        self.assertEqual(self.requestPageConsulta.status_code, 200)

    def testCadastroPost(self):
        """ teste de método post da página de cadastro de funcionário """
        self.assertEqual(self.requestCadastro.status_code, 302)

    def testEditarPost(self):
        """ teste de método post da página de edição de funcionário """
        self.assertEqual(self.requestEdicao.status_code, 302)    