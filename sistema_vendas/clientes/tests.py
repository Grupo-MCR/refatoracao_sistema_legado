from django.test import TestCase, Client as DjangoClient
from django.urls import reverse
from .models import Cliente
from .logic import ClienteLogic
import json


class ClienteModelTest(TestCase):
    """Testes do modelo Cliente"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.cliente_data = {
            'nome': 'João da Silva',
            'rg': '12.345.678-9',
            'cpf': '12345678901',
            'email': 'joao@email.com',
            'telefone': '1133334444',
            'celular': '11987654321',
            'cep': '01234567',
            'endereco': 'Rua Teste',
            'numero': 123,
            'complemento': 'Apto 45',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'uf': 'SP'
        }
    
    def test_criar_cliente_sucesso(self):
        """Teste de criação de cliente com sucesso"""
        cliente = Cliente.objects.create(**self.cliente_data)
        
        self.assertEqual(cliente.nome, 'João da Silva')
        self.assertEqual(cliente.cpf, '12345678901')
        self.assertEqual(cliente.email, 'joao@email.com')
        self.assertEqual(cliente.cidade, 'São Paulo')
        self.assertIsNotNone(cliente.id)
    
    def test_cpf_unico(self):
        """Teste de validação de CPF único"""
        Cliente.objects.create(**self.cliente_data)
        
        # Tentar criar outro cliente com o mesmo CPF
        with self.assertRaises(Exception):
            Cliente.objects.create(**self.cliente_data)
    
    def test_campos_opcionais(self):
        """Teste de criação com apenas campos obrigatórios"""
        cliente = Cliente.objects.create(
            nome='Maria Santos',
            cpf='98765432100'
        )
        
        self.assertEqual(cliente.nome, 'Maria Santos')
        self.assertIsNone(cliente.email)
        self.assertIsNone(cliente.telefone)
        self.assertIsNone(cliente.endereco)
    
    def test_atualizacao_cliente(self):
        """Teste de atualização de dados do cliente"""
        cliente = Cliente.objects.create(**self.cliente_data)
        
        cliente.nome = 'João Silva Atualizado'
        cliente.email = 'joao.novo@email.com'
        cliente.save()
        
        cliente_atualizado = Cliente.objects.get(id=cliente.id)
        self.assertEqual(cliente_atualizado.nome, 'João Silva Atualizado')
        self.assertEqual(cliente_atualizado.email, 'joao.novo@email.com')
    
    def test_delecao_cliente(self):
        """Teste de deleção de cliente"""
        cliente = Cliente.objects.create(**self.cliente_data)
        cliente_id = cliente.id
        
        cliente.delete()
        
        with self.assertRaises(Cliente.DoesNotExist):
            Cliente.objects.get(id=cliente_id)


class ClienteLogicTest(TestCase):
    """Testes da lógica de negócio de Cliente"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.cliente_data = {
            'nome': 'João da Silva',
            'rg': '12.345.678-9',
            'cpf': '12345678901',
            'email': 'joao@email.com',
            'telefone': '1133334444',
            'celular': '11987654321',
            'cep': '01234567',
            'endereco': 'Rua Teste',
            'numero': 123,
            'complemento': 'Apto 45',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'uf': 'SP'
        }
    
    def test_criar_cliente_logic(self):
        """Teste de criação via lógica de negócio"""
        resultado = ClienteLogic.criar_cliente(self.cliente_data)
        
        self.assertIsNotNone(resultado['id'])
        self.assertEqual(resultado['nome'], 'João da Silva')
        self.assertEqual(resultado['cpf'], '12345678901')
    
    def test_criar_cliente_cpf_duplicado(self):
        """Teste de erro ao criar cliente com CPF duplicado"""
        ClienteLogic.criar_cliente(self.cliente_data)
        
        with self.assertRaises(Exception) as context:
            ClienteLogic.criar_cliente(self.cliente_data)
        
        self.assertIn('CPF já cadastrado', str(context.exception))
    
    def test_listar_clientes(self):
        """Teste de listagem de clientes"""
        ClienteLogic.criar_cliente(self.cliente_data)
        
        cliente_data2 = self.cliente_data.copy()
        cliente_data2['nome'] = 'Maria Santos'
        cliente_data2['cpf'] = '98765432100'
        ClienteLogic.criar_cliente(cliente_data2)
        
        clientes = ClienteLogic.listar_clientes()
        
        self.assertEqual(len(clientes), 2)
    
    def test_listar_clientes_com_busca(self):
        """Teste de busca de clientes"""
        ClienteLogic.criar_cliente(self.cliente_data)
        
        cliente_data2 = self.cliente_data.copy()
        cliente_data2['nome'] = 'Maria Santos'
        cliente_data2['cpf'] = '98765432100'
        ClienteLogic.criar_cliente(cliente_data2)
        
        # Buscar por nome
        clientes = ClienteLogic.listar_clientes(search='João')
        self.assertEqual(len(clientes), 1)
        self.assertEqual(clientes[0]['nome'], 'João da Silva')
        
        # Buscar por cidade
        clientes = ClienteLogic.listar_clientes(search='São Paulo')
        self.assertEqual(len(clientes), 2)
    
    def test_obter_cliente(self):
        """Teste de obtenção de cliente específico"""
        resultado_criacao = ClienteLogic.criar_cliente(self.cliente_data)
        cliente_id = resultado_criacao['id']
        
        cliente = ClienteLogic.obter_cliente(cliente_id)
        
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente['nome'], 'João da Silva')
        self.assertEqual(cliente['cpf'], '12345678901')
    
    def test_obter_cliente_inexistente(self):
        """Teste de obtenção de cliente que não existe"""
        cliente = ClienteLogic.obter_cliente(99999)
        
        self.assertIsNone(cliente)
    
    def test_atualizar_cliente(self):
        """Teste de atualização de cliente"""
        resultado_criacao = ClienteLogic.criar_cliente(self.cliente_data)
        cliente_id = resultado_criacao['id']
        
        dados_atualizacao = {
            'nome': 'João Silva Atualizado',
            'email': 'joao.novo@email.com',
            'telefone': '1144445555'
        }
        
        resultado = ClienteLogic.atualizar_cliente(cliente_id, dados_atualizacao)
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['nome'], 'João Silva Atualizado')
        
        # Verificar se foi realmente atualizado
        cliente = ClienteLogic.obter_cliente(cliente_id)
        self.assertEqual(cliente['nome'], 'João Silva Atualizado')
        self.assertEqual(cliente['email'], 'joao.novo@email.com')
    
    def test_atualizar_cliente_cpf_duplicado(self):
        """Teste de erro ao atualizar com CPF duplicado"""
        # Criar primeiro cliente
        resultado1 = ClienteLogic.criar_cliente(self.cliente_data)
        
        # Criar segundo cliente
        cliente_data2 = self.cliente_data.copy()
        cliente_data2['nome'] = 'Maria Santos'
        cliente_data2['cpf'] = '98765432100'
        resultado2 = ClienteLogic.criar_cliente(cliente_data2)
        
        # Tentar atualizar segundo cliente com CPF do primeiro
        with self.assertRaises(Exception) as context:
            ClienteLogic.atualizar_cliente(resultado2['id'], {'cpf': '12345678901'})
        
        self.assertIn('CPF já cadastrado', str(context.exception))
    
    def test_deletar_cliente(self):
        """Teste de deleção de cliente"""
        resultado_criacao = ClienteLogic.criar_cliente(self.cliente_data)
        cliente_id = resultado_criacao['id']
        
        resultado = ClienteLogic.deletar_cliente(cliente_id)
        
        self.assertTrue(resultado)
        
        # Verificar se foi realmente deletado
        cliente = ClienteLogic.obter_cliente(cliente_id)
        self.assertIsNone(cliente)
    
    def test_deletar_cliente_inexistente(self):
        """Teste de deleção de cliente que não existe"""
        resultado = ClienteLogic.deletar_cliente(99999)
        
        self.assertFalse(resultado)
    
    def test_validar_cpf_valido(self):
        """Teste de validação de CPF válido"""
        cpf_valido = '11144477735'  # CPF válido
        self.assertTrue(ClienteLogic.validar_cpf(cpf_valido))
    
    def test_validar_cpf_invalido(self):
        """Teste de validação de CPF inválido"""
        # CPF com dígitos verificadores incorretos
        cpf_invalido = '12345678901'
        self.assertFalse(ClienteLogic.validar_cpf(cpf_invalido))
        
        # CPF com todos dígitos iguais
        cpf_invalido2 = '11111111111'
        self.assertFalse(ClienteLogic.validar_cpf(cpf_invalido2))
        
        # CPF com tamanho incorreto
        cpf_invalido3 = '123456789'
        self.assertFalse(ClienteLogic.validar_cpf(cpf_invalido3))


class ClienteAPITest(TestCase):
    """Testes das APIs de Cliente"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.client = DjangoClient()
        self.cliente_data = {
            'nome': 'João da Silva',
            'rg': '12.345.678-9',
            'cpf': '12345678901',
            'email': 'joao@email.com',
            'telefone': '1133334444',
            'celular': '11987654321',
            'cep': '01234567',
            'endereco': 'Rua Teste',
            'numero': 123,
            'complemento': 'Apto 45',
            'bairro': 'Centro',
            'cidade': 'São Paulo',
            'uf': 'SP'
        }
    
    def test_api_criar_cliente(self):
        """Teste da API de criação de cliente"""
        response = self.client.post(
            '/clientes/api/criar/',
            data=json.dumps(self.cliente_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('cliente', data)
    
    def test_api_listar_clientes(self):
        """Teste da API de listagem de clientes"""
        # Criar alguns clientes primeiro
        ClienteLogic.criar_cliente(self.cliente_data)
        
        response = self.client.get('/clientes/api/listar/')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('clientes', data)
        self.assertGreater(len(data['clientes']), 0)
    
    def test_api_obter_cliente(self):
        """Teste da API de obtenção de cliente"""
        resultado = ClienteLogic.criar_cliente(self.cliente_data)
        cliente_id = resultado['id']
        
        response = self.client.get(f'/clientes/api/obter/{cliente_id}/')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('cliente', data)
        self.assertEqual(data['cliente']['nome'], 'João da Silva')
    
    def test_api_atualizar_cliente(self):
        """Teste da API de atualização de cliente"""
        resultado = ClienteLogic.criar_cliente(self.cliente_data)
        cliente_id = resultado['id']
        
        dados_atualizacao = {
            'nome': 'João Silva Atualizado',
            'email': 'joao.novo@email.com'
        }
        
        response = self.client.put(
            f'/clientes/api/atualizar/{cliente_id}/',
            data=json.dumps(dados_atualizacao),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_api_deletar_cliente(self):
        """Teste da API de deleção de cliente"""
        resultado = ClienteLogic.criar_cliente(self.cliente_data)
        cliente_id = resultado['id']
        
        response = self.client.delete(f'/clientes/api/deletar/{cliente_id}/')
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])


class ClienteIntegrationTest(TestCase):
    """Testes de integração do fluxo completo"""
    
    def test_fluxo_completo_crud(self):
        """Teste do fluxo completo de CRUD de cliente"""
        # 1. Criar cliente
        dados_cliente = {
            'nome': 'Teste Integração',
            'cpf': '12345678901',
            'email': 'teste@email.com',
            'cidade': 'São Paulo'
        }
        
        resultado_criacao = ClienteLogic.criar_cliente(dados_cliente)
        cliente_id = resultado_criacao['id']
        
        self.assertIsNotNone(cliente_id)
        
        # 2. Listar e verificar se o cliente está lá
        clientes = ClienteLogic.listar_clientes()
        self.assertEqual(len(clientes), 1)
        
        # 3. Obter cliente específico
        cliente = ClienteLogic.obter_cliente(cliente_id)
        self.assertEqual(cliente['nome'], 'Teste Integração')
        
        # 4. Atualizar cliente
        ClienteLogic.atualizar_cliente(cliente_id, {'nome': 'Teste Atualizado'})
        cliente_atualizado = ClienteLogic.obter_cliente(cliente_id)
        self.assertEqual(cliente_atualizado['nome'], 'Teste Atualizado')
        
        # 5. Deletar cliente
        ClienteLogic.deletar_cliente(cliente_id)
        cliente_deletado = ClienteLogic.obter_cliente(cliente_id)
        self.assertIsNone(cliente_deletado)
    
    def test_busca_multiplos_criterios(self):
        """Teste de busca com múltiplos critérios"""
        # Criar vários clientes
        ClienteLogic.criar_cliente({
            'nome': 'João Silva',
            'cpf': '11111111111',
            'cidade': 'São Paulo'
        })
        
        ClienteLogic.criar_cliente({
            'nome': 'Maria Santos',
            'cpf': '22222222222',
            'cidade': 'Rio de Janeiro'
        })
        
        ClienteLogic.criar_cliente({
            'nome': 'Pedro Silva',
            'cpf': '33333333333',
            'cidade': 'São Paulo'
        })
        
        # Buscar por sobrenome
        resultado = ClienteLogic.listar_clientes(search='Silva')
        self.assertEqual(len(resultado), 2)
        
        # Buscar por cidade
        resultado = ClienteLogic.listar_clientes(search='São Paulo')
        self.assertEqual(len(resultado), 2)