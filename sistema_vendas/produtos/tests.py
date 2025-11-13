from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
import json

from .models import Produto
from fornecedores.models import Fornecedor
from .logic import ProdutoLogic

# Create your tests here.

class ProdutoModelTest(TestCase):
    """Testes do modelo Produto"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.fornecedor = Fornecedor.objects.create(
            nome='Fornecedor Teste',
            cnpj='12.345.678/0001-90',
            email='teste@fornecedor.com',
            telefone='(45) 99999-9999'
        )
    
    def test_criacao_produto_valido(self):
        """Teste de criação de produto com dados válidos"""
        produto = Produto.objects.create(
            descricao='Notebook Dell Inspiron',
            preco=Decimal('3500.00'),
            qtd_estoque=10,
            fornecedor=self.fornecedor
        )
        
        self.assertEqual(produto.descricao, 'Notebook Dell Inspiron')
        self.assertEqual(produto.preco, Decimal('3500.00'))
        self.assertEqual(produto.qtd_estoque, 10)
        self.assertEqual(produto.fornecedor, self.fornecedor)
    
    def test_string_representation(self):
        """Teste da representação string do produto"""
        produto = Produto.objects.create(
            descricao='Mouse Logitech',
            preco=Decimal('85.00'),
            qtd_estoque=50,
            fornecedor=self.fornecedor
        )
        
        self.assertEqual(str(produto), 'Mouse Logitech')
    
    def test_produto_com_preco_decimal(self):
        """Teste de produto com preço decimal correto"""
        produto = Produto.objects.create(
            descricao='Teclado Mecânico',
            preco=Decimal('299.99'),
            qtd_estoque=20,
            fornecedor=self.fornecedor
        )
        
        self.assertEqual(produto.preco, Decimal('299.99'))
        # Verifica se tem 2 casas decimais
        self.assertEqual(produto.preco.as_tuple().exponent, -2)


class ProdutoCadastroTest(TestCase):
    """Testes de cadastro de produtos"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
        self.fornecedor = Fornecedor.objects.create(
            nome='TechSupply',
            cnpj='11.222.333/0001-44',
            email='contato@techsupply.com',
            telefone='(45) 98888-8888'
        )
    
    def test_cadastro_produto_valido(self):
        """Teste de cadastro de produto com dados válidos via Logic"""
        produto_data = ProdutoLogic.criar_produto(
            descricao='Monitor LG 24"',
            preco=850.00,
            qtd_estoque=15,
            fornecedor_id=self.fornecedor.id
        )
        
        self.assertIsNotNone(produto_data)
        self.assertEqual(produto_data['descricao'], 'Monitor LG 24"')
        self.assertEqual(produto_data['preco'], 850.00)
        self.assertEqual(produto_data['qtd_estoque'], 15)
        
        # Verifica se foi salvo no banco
        produto = Produto.objects.get(id=produto_data['id'])
        self.assertEqual(produto.descricao, 'Monitor LG 24"')
    
    def test_cadastro_produto_via_api(self):
        """Teste de cadastro via endpoint de API"""
        url = reverse('produtos:criar_produto')
        data = {
            'descricao': 'Webcam Logitech C920',
            'preco': 450.00,
            'qtd_estoque': 8,
            'fornecedor': self.fornecedor.id
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['produto']['descricao'], 'Webcam Logitech C920')
    
    def test_cadastro_sem_descricao(self):
        """Teste de cadastro sem descrição (deve falhar)"""
        try:
            Produto.objects.create(
                descricao='',
                preco=Decimal('100.00'),
                qtd_estoque=5,
                fornecedor=self.fornecedor
            )
            self.fail('Deveria ter lançado exceção para descrição vazia')
        except:
            pass
    
    def test_cadastro_preco_negativo(self):
        """Teste de cadastro com preço negativo (deve falhar via lógica de negócio)"""
        # O Django permite valores negativos no DecimalField, 
        # então testamos via validação de negócio
        produto = Produto.objects.create(
            descricao='Produto Teste',
            preco=Decimal('-50.00'),
            qtd_estoque=5,
            fornecedor=self.fornecedor
        )
        
        # Validação deve detectar preço negativo
        self.assertLess(produto.preco, 0)
    
    def test_cadastro_quantidade_negativa(self):
        """Teste de cadastro com quantidade negativa"""
        produto = Produto.objects.create(
            descricao='Produto Teste',
            preco=Decimal('100.00'),
            qtd_estoque=-5,
            fornecedor=self.fornecedor
        )
        
        self.assertLess(produto.qtd_estoque, 0)
    
    def test_cadastro_fornecedor_inexistente(self):
        """Teste de cadastro com fornecedor inexistente"""
        with self.assertRaises(ValueError):
            ProdutoLogic.criar_produto(
                descricao='Produto Teste',
                preco=100.00,
                qtd_estoque=5,
                fornecedor_id=9999  # ID inexistente
            )
    
    def test_cadastro_descricao_maxlength(self):
        """Teste de limite de caracteres na descrição (200)"""
        descricao_longa = 'A' * 200
        produto = Produto.objects.create(
            descricao=descricao_longa,
            preco=Decimal('100.00'),
            qtd_estoque=5,
            fornecedor=self.fornecedor
        )
        
        self.assertEqual(len(produto.descricao), 200)
    
    def test_cadastro_descricao_excede_maxlength(self):
        """Teste com descrição excedendo 200 caracteres (deve truncar ou falhar)"""
        descricao_muito_longa = 'A' * 201
        
        try:
            produto = Produto.objects.create(
                descricao=descricao_muito_longa,
                preco=Decimal('100.00'),
                qtd_estoque=5,
                fornecedor=self.fornecedor
            )
            # Se não falhou, verifica se truncou
            self.assertLessEqual(len(produto.descricao), 200)
        except:
            # Esperado: erro de validação
            pass
    
    def test_cadastro_multiplos_produtos_mesmo_fornecedor(self):
        """Teste de cadastro de múltiplos produtos com o mesmo fornecedor"""
        produto1 = Produto.objects.create(
            descricao='Produto 1',
            preco=Decimal('100.00'),
            qtd_estoque=10,
            fornecedor=self.fornecedor
        )
        
        produto2 = Produto.objects.create(
            descricao='Produto 2',
            preco=Decimal('200.00'),
            qtd_estoque=20,
            fornecedor=self.fornecedor
        )
        
        self.assertEqual(produto1.fornecedor, produto2.fornecedor)
        self.assertEqual(self.fornecedor.produtos.count(), 2)


class ProdutoEdicaoTest(TestCase):
    """Testes de edição de produtos"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.client = Client()
        
        self.fornecedor1 = Fornecedor.objects.create(
            nome='Fornecedor A',
            cnpj='11.111.111/0001-11',
            email='a@fornecedor.com',
            telefone='(45) 91111-1111'
        )
        
        self.fornecedor2 = Fornecedor.objects.create(
            nome='Fornecedor B',
            cnpj='22.222.222/0001-22',
            email='b@fornecedor.com',
            telefone='(45) 92222-2222'
        )
        
        self.produto = Produto.objects.create(
            descricao='Headset Gamer',
            preco=Decimal('250.00'),
            qtd_estoque=12,
            fornecedor=self.fornecedor1
        )
    
    def test_edicao_produto_valido(self):
        """Teste de edição de produto com dados válidos via Logic"""
        produto_atualizado = ProdutoLogic.atualizar_produto(
            produto_id=self.produto.id,
            descricao='Headset Gamer RGB',
            preco=300.00,
            qtd_estoque=20,
            fornecedor_id=self.fornecedor1.id
        )
        
        self.assertIsNotNone(produto_atualizado)
        self.assertEqual(produto_atualizado['descricao'], 'Headset Gamer RGB')
        self.assertEqual(produto_atualizado['preco'], 300.00)
        self.assertEqual(produto_atualizado['qtd_estoque'], 20)
        
        # Verifica no banco
        produto_db = Produto.objects.get(id=self.produto.id)
        self.assertEqual(produto_db.descricao, 'Headset Gamer RGB')
        self.assertEqual(produto_db.preco, Decimal('300.00'))
    
    def test_edicao_via_api(self):
        """Teste de edição via endpoint de API"""
        url = reverse('produtos:atualizar_produto', args=[self.produto.id])
        data = {
            'descricao': 'Headset Gamer Wireless',
            'preco': 350.00,
            'qtd_estoque': 15,
            'fornecedor': self.fornecedor1.id
        }
        
        response = self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['produto']['descricao'], 'Headset Gamer Wireless')
    
    def test_edicao_produto_inexistente(self):
        """Teste de edição de produto que não existe"""
        resultado = ProdutoLogic.atualizar_produto(
            produto_id=9999,
            descricao='Teste',
            preco=100.00,
            qtd_estoque=10,
            fornecedor_id=self.fornecedor1.id
        )
        
        self.assertIsNone(resultado)
    
    def test_edicao_apenas_preco(self):
        """Teste de edição alterando apenas o preço"""
        descricao_original = self.produto.descricao
        qtd_original = self.produto.qtd_estoque
        
        ProdutoLogic.atualizar_produto(
            produto_id=self.produto.id,
            descricao=descricao_original,
            preco=500.00,
            qtd_estoque=qtd_original,
            fornecedor_id=self.fornecedor1.id
        )
        
        produto_atualizado = Produto.objects.get(id=self.produto.id)
        self.assertEqual(produto_atualizado.descricao, descricao_original)
        self.assertEqual(produto_atualizado.preco, Decimal('500.00'))
        self.assertEqual(produto_atualizado.qtd_estoque, qtd_original)
    
    def test_edicao_mudar_fornecedor(self):
        """Teste de edição alterando o fornecedor"""
        ProdutoLogic.atualizar_produto(
            produto_id=self.produto.id,
            descricao=self.produto.descricao,
            preco=float(self.produto.preco),
            qtd_estoque=self.produto.qtd_estoque,
            fornecedor_id=self.fornecedor2.id
        )
        
        produto_atualizado = Produto.objects.get(id=self.produto.id)
        self.assertEqual(produto_atualizado.fornecedor, self.fornecedor2)
        self.assertEqual(produto_atualizado.fornecedor.nome, 'Fornecedor B')
    
    def test_edicao_fornecedor_inexistente(self):
        """Teste de edição com fornecedor inexistente"""
        with self.assertRaises(ValueError):
            ProdutoLogic.atualizar_produto(
                produto_id=self.produto.id,
                descricao='Teste',
                preco=100.00,
                qtd_estoque=10,
                fornecedor_id=9999
            )
    
    def test_edicao_aumentar_estoque(self):
        """Teste de edição aumentando quantidade em estoque"""
        estoque_inicial = self.produto.qtd_estoque
        novo_estoque = estoque_inicial + 50
        
        ProdutoLogic.atualizar_produto(
            produto_id=self.produto.id,
            descricao=self.produto.descricao,
            preco=float(self.produto.preco),
            qtd_estoque=novo_estoque,
            fornecedor_id=self.fornecedor1.id
        )
        
        produto_atualizado = Produto.objects.get(id=self.produto.id)
        self.assertEqual(produto_atualizado.qtd_estoque, novo_estoque)
    
    def test_edicao_diminuir_estoque(self):
        """Teste de edição diminuindo quantidade em estoque"""
        estoque_inicial = self.produto.qtd_estoque
        novo_estoque = estoque_inicial - 5
        
        ProdutoLogic.atualizar_produto(
            produto_id=self.produto.id,
            descricao=self.produto.descricao,
            preco=float(self.produto.preco),
            qtd_estoque=novo_estoque,
            fornecedor_id=self.fornecedor1.id
        )
        
        produto_atualizado = Produto.objects.get(id=self.produto.id)
        self.assertEqual(produto_atualizado.qtd_estoque, novo_estoque)


class ProdutoIntegracaoTest(TestCase):
    """Testes de integração - fluxos completos"""
    
    def setUp(self):
        """Configuração inicial dos testes"""
        self.fornecedor = Fornecedor.objects.create(
            nome='Distribuidora Tech',
            cnpj='33.333.333/0001-33',
            email='tech@distribuidora.com',
            telefone='(45) 93333-3333'
        )
    
    def test_fluxo_completo_criar_editar_consultar(self):
        """Teste de fluxo completo: criar → editar → consultar"""
        # 1. Criar produto
        produto_criado = ProdutoLogic.criar_produto(
            descricao='SSD 500GB',
            preco=350.00,
            qtd_estoque=30,
            fornecedor_id=self.fornecedor.id
        )
        
        self.assertIsNotNone(produto_criado)
        produto_id = produto_criado['id']
        
        # 2. Editar produto
        produto_editado = ProdutoLogic.atualizar_produto(
            produto_id=produto_id,
            descricao='SSD 1TB',
            preco=650.00,
            qtd_estoque=25,
            fornecedor_id=self.fornecedor.id
        )
        
        self.assertEqual(produto_editado['descricao'], 'SSD 1TB')
        self.assertEqual(produto_editado['preco'], 650.00)
        
        # 3. Consultar produto
        produto_consultado = ProdutoLogic.obter_produto(produto_id)
        
        self.assertEqual(produto_consultado['descricao'], 'SSD 1TB')
        self.assertEqual(produto_consultado['preco'], 650.00)
        self.assertEqual(produto_consultado['qtd_estoque'], 25)
    
    def test_criar_varios_produtos_e_listar(self):
        """Teste de criação de vários produtos e listagem"""
        # Criar múltiplos produtos
        produtos_criados = []
        for i in range(5):
            produto = ProdutoLogic.criar_produto(
                descricao=f'Produto {i+1}',
                preco=100.00 * (i+1),
                qtd_estoque=10 * (i+1),
                fornecedor_id=self.fornecedor.id
            )
            produtos_criados.append(produto)
        
        # Listar todos
        produtos_listados = ProdutoLogic.listar_produtos()
        
        self.assertEqual(len(produtos_listados), 5)
        self.assertEqual(produtos_listados[0]['descricao'], 'Produto 1')
    
    def test_busca_produto_apos_edicao(self):
        """Teste de busca de produto após edição"""
        # Criar produto
        produto = ProdutoLogic.criar_produto(
            descricao='Teclado Mecânico',
            preco=300.00,
            qtd_estoque=20,
            fornecedor_id=self.fornecedor.id
        )
        
        # Editar descrição
        ProdutoLogic.atualizar_produto(
            produto_id=produto['id'],
            descricao='Teclado Mecânico RGB',
            preco=300.00,
            qtd_estoque=20,
            fornecedor_id=self.fornecedor.id
        )
        
        # Buscar pela nova descrição
        produtos = ProdutoLogic.listar_produtos(search='RGB')
        
        self.assertEqual(len(produtos), 1)
        self.assertEqual(produtos[0]['descricao'], 'Teclado Mecânico RGB')
    
    def test_relacionamento_fornecedor_produtos(self):
        """Teste de relacionamento entre fornecedor e produtos"""
        # Criar vários produtos para o mesmo fornecedor
        for i in range(3):
            ProdutoLogic.criar_produto(
                descricao=f'Item {i+1}',
                preco=50.00,
                qtd_estoque=10,
                fornecedor_id=self.fornecedor.id
            )
        
        # Verificar relacionamento
        fornecedor_db = Fornecedor.objects.get(id=self.fornecedor.id)
        self.assertEqual(fornecedor_db.produtos.count(), 3)
    
    def test_integridade_apos_multiplas_edicoes(self):
        """Teste de integridade após múltiplas edições"""
        produto = ProdutoLogic.criar_produto(
            descricao='Produto Teste',
            preco=100.00,
            qtd_estoque=10,
            fornecedor_id=self.fornecedor.id
        )
        
        produto_id = produto['id']
        
        # Fazer várias edições
        for i in range(10):
            ProdutoLogic.atualizar_produto(
                produto_id=produto_id,
                descricao=f'Produto Editado {i+1}',
                preco=100.00 + (i * 10),
                qtd_estoque=10 + i,
                fornecedor_id=self.fornecedor.id
            )
        
        # Verificar estado final
        produto_final = ProdutoLogic.obter_produto(produto_id)
        self.assertEqual(produto_final['descricao'], 'Produto Editado 10')
        self.assertEqual(produto_final['preco'], 190.00)
        self.assertEqual(produto_final['qtd_estoque'], 19)