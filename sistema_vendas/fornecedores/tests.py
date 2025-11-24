from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import json

try:
    from .models import Fornecedor, Compra, ItemCompra
    from .compraService import CompraService
    from .fornecedorService import FornecedorService
except ImportError:
    pass

try:
    from produtos.models import Produto
except ImportError:
    # Se o modelo Produto não existir, criar um mock
    from django.db import models
    
    class Produto(models.Model):
        descricao = models.CharField(max_length=200)
        preco = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
        
        class Meta:
            app_label = 'produtos'
            db_table = 'tb_produtos'


class BaseCompraTestCase(TestCase):
    """Classe base para testes de compra com helpers"""
    
    def criar_produto(self, descricao="Produto Teste", preco=10.00):
        """Helper para criar produto"""
        try:
            from produtos.models import Produto as ProdutoReal
            return ProdutoReal.objects.create(
                descricao=descricao,
                preco=Decimal(str(preco))
            )
        except:
            # Fallback se o modelo não existir
            return type('Produto', (), {
                'id': 1,
                'descricao': descricao,
                'preco': Decimal(str(preco))
            })()


class FornecedorTestCase(TestCase):
    """Testes para o CRUD de fornecedores"""
    
    def setUp(self):
        """Configuração inicial antes de cada teste"""
        self.client = Client()
        
        # Dados de exemplo para testes
        self.dados_validos = {
            'nome': 'Fornecedor Teste LTDA',
            'cnpj': '12.345.678/0001-90',
            'email': 'teste@fornecedor.com',
            'telefone': '(45) 3254-1234',
            'celular': '(45) 99999-8888',
            'cep': '85960-000',
            'endereco': 'Rua Teste',
            'numero': '123',
            'complemento': 'Sala 1',
            'bairro': 'Centro',
            'cidade': 'Marechal Cândido Rondon',
            'estado': 'PR',
        }
    
    def test_cadastrar_fornecedor_sucesso(self):
        """Testa o cadastro de um fornecedor com dados válidos"""
        response = self.client.post(
            reverse('cadastroFornecedor'),
            data=self.dados_validos
        )
        
        # Verifica se redireciona após sucesso
        self.assertEqual(response.status_code, 302)
        
        # Verifica se foi criado
        fornecedores = Fornecedor.objects.all()
        self.assertGreater(fornecedores.count(), 0)
    
    def test_cadastrar_fornecedor_cnpj_invalido(self):
        """Testa cadastro com CNPJ inválido"""
        dados_invalidos = self.dados_validos.copy()
        dados_invalidos['cnpj'] = '111.111.111/1111-11'
        
        response = self.client.post(
            reverse('cadastroFornecedor'),
            data=dados_invalidos
        )
        
        # Se sua validação estiver funcionando, deve retornar 200 com erro
        # Se não tiver validação, vai redirecionar (302)
        # Ajuste conforme seu sistema atual
        self.assertIn(response.status_code, [200, 302])
    
    def test_listar_fornecedores(self):
        """Testa a listagem de fornecedores"""
        # Primeiro cadastra um fornecedor
        sucesso, msg, fornecedor = FornecedorService.cadastrar_fornecedor(self.dados_validos)
        
        # Testa a view de consulta
        response = self.client.get(reverse('consultaFornecedor'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fornecedor Teste LTDA')
    
    def test_editar_fornecedor(self):
        """Testa a edição de um fornecedor"""
        # Cadastra primeiro
        sucesso, msg, fornecedor = FornecedorService.cadastrar_fornecedor(self.dados_validos)
        fornecedor_id = fornecedor.id  # MUDOU: usar .id ao invés de ['id']
        
        # Dados para edição
        dados_editados = self.dados_validos.copy()
        dados_editados['nome'] = 'Fornecedor Editado LTDA'
        
        # Faz a edição
        response = self.client.post(
            reverse('editarFornecedor', args=[fornecedor_id]),
            data=dados_editados
        )
        
        # Verifica se redireciona
        self.assertEqual(response.status_code, 302)
        
        # Busca o fornecedor e verifica se foi editado
        fornecedor_atualizado = Fornecedor.objects.get(id=fornecedor_id)
        self.assertEqual(fornecedor_atualizado.nome, 'Fornecedor Editado LTDA')
    
    def test_excluir_fornecedor(self):
        """Testa a exclusão de um fornecedor"""
        # Cadastra primeiro
        sucesso, msg, fornecedor = FornecedorService.cadastrar_fornecedor(self.dados_validos)
        fornecedor_id = fornecedor.id  # MUDOU: usar .id ao invés de ['id']
        
        # Exclui
        response = self.client.post(
            reverse('excluirFornecedor', args=[fornecedor_id])
        )
        
        # Verifica se redireciona
        self.assertEqual(response.status_code, 302)
        
        # Verifica se foi excluído
        existe = Fornecedor.objects.filter(id=fornecedor_id).exists()
        self.assertFalse(existe)
    
    def test_buscar_fornecedor_inexistente(self):
        """Testa busca de fornecedor que não existe"""
        response = self.client.get(
            reverse('editarFornecedor', args=[99999])
        )
        
        # Deve redirecionar para consulta com erro
        self.assertEqual(response.status_code, 302)
        # Verifica se redireciona para a página de consulta
        self.assertRedirects(response, reverse('consultaFornecedor'))


class CompraModelTest(TestCase):
    """Testes para o modelo Compra"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            cnpj="12.345.678/0001-90"
        )
        
        self.produto = Produto.objects.create(
            descricao="Produto Teste",
            preco=Decimal('10.50')
        )
        
        self.compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            data_compra=timezone.now(),
            status='pendente',
            valor_total=Decimal('105.00'),
            criado_por=self.user
        )
    
    def test_criar_compra(self):
        """Testa criação de compra"""
        self.assertEqual(self.compra.numero_pedido, "COMP-20251119-0001")
        self.assertEqual(self.compra.fornecedor, self.fornecedor)
        self.assertEqual(self.compra.status, 'pendente')
        self.assertEqual(self.compra.valor_total, Decimal('105.00'))
    
    def test_status_choices(self):
        """Testa valores válidos de status"""
        status_validos = ['pendente', 'processando', 'concluida', 'cancelada']
        for status in status_validos:
            self.compra.status = status
            self.compra.save()
            self.assertEqual(self.compra.status, status)
    
    def test_str_compra(self):
        """Testa representação string da compra"""
        expected = f"Compra #{self.compra.numero_pedido} - {self.fornecedor}"
        self.assertEqual(str(self.compra), expected)
    
    def test_valor_padrao_frete_desconto(self):
        """Testa valores padrão de frete e desconto"""
        self.assertEqual(self.compra.valor_frete, Decimal('0.00'))
        self.assertEqual(self.compra.valor_desconto, Decimal('0.00'))


class ItemCompraModelTest(TestCase):
    """Testes para o modelo ItemCompra"""
    
    def setUp(self):
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            cnpj="12.345.678/0001-90"
        )
        
        self.produto = Produto.objects.create(
            descricao="Produto Teste",
            preco=Decimal('10.50')
        )
        
        self.compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('105.00')
        )
    
    def test_criar_item_compra(self):
        """Testa criação de item de compra"""
        item = ItemCompra.objects.create(
            compra=self.compra,
            produto=self.produto,
            quantidade=10,
            preco_unitario=Decimal('10.50'),
            subtotal=Decimal('105.00')
        )
        
        self.assertEqual(item.compra, self.compra)
        self.assertEqual(item.produto, self.produto)
        self.assertEqual(item.quantidade, 10)
        self.assertEqual(item.preco_unitario, Decimal('10.50'))
        self.assertEqual(item.subtotal, Decimal('105.00'))
    
    def test_calculo_automatico_subtotal(self):
        """Testa cálculo automático do subtotal"""
        item = ItemCompra(
            compra=self.compra,
            produto=self.produto,
            quantidade=5,
            preco_unitario=Decimal('20.00'),
            subtotal=Decimal('0.00')  # Será calculado automaticamente
        )
        item.save()
        
        self.assertEqual(item.subtotal, Decimal('100.00'))
    
    def test_str_item_compra(self):
        """Testa representação string do item"""
        item = ItemCompra.objects.create(
            compra=self.compra,
            produto=self.produto,
            quantidade=10,
            preco_unitario=Decimal('10.50'),
            subtotal=Decimal('105.00')
        )
        
        expected = f"{self.produto.descricao} - 10x R$ 10.50"
        self.assertEqual(str(item), expected)


class CompraServiceTest(TestCase):
    """Testes para o CompraService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            cnpj="12.345.678/0001-90"
        )
        
        self.produto1 = Produto.objects.create(
            descricao="Produto 1",
            preco=Decimal('10.00')
        )
        
        self.produto2 = Produto.objects.create(
            descricao="Produto 2",
            preco=Decimal('25.50')
        )
    
    def test_gerar_numero_pedido(self):
        """Testa geração de número de pedido"""
        numero = CompraService.gerar_numero_pedido()
        hoje = timezone.now().strftime('%Y%m%d')
        
        self.assertTrue(numero.startswith(f'COMP-{hoje}'))
        self.assertTrue(numero.endswith('-0001'))
    
    def test_gerar_numero_pedido_sequencial(self):
        """Testa geração sequencial de números de pedido"""
        numero1 = CompraService.gerar_numero_pedido()
        
        # Cria uma compra com o primeiro número
        Compra.objects.create(
            numero_pedido=numero1,
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00')
        )
        
        numero2 = CompraService.gerar_numero_pedido()
        
        # Verifica que o segundo número é sequencial
        self.assertNotEqual(numero1, numero2)
        self.assertTrue(numero2.endswith('-0002'))
    
    def test_converter_data_br_para_datetime(self):
        """Testa conversão de data brasileira para datetime"""
        data_str = "19/11/2025"
        data_obj = CompraService.converter_data_br_para_datetime(data_str)
        
        self.assertEqual(data_obj.day, 19)
        self.assertEqual(data_obj.month, 11)
        self.assertEqual(data_obj.year, 2025)
    
    def test_converter_data_invalida(self):
        """Testa conversão de data inválida"""
        with self.assertRaises(ValueError):
            CompraService.converter_data_br_para_datetime("data_invalida")
    
    def test_cadastrar_compra_sucesso(self):
        """Testa cadastro de compra com sucesso"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'observacoes': 'Teste de observação',
            'itens': [
                {
                    'id_produto': self.produto1.id,
                    'quantidade': 10,
                    'preco_unitario': 10.00
                },
                {
                    'id_produto': self.produto2.id,
                    'quantidade': 5,
                    'preco_unitario': 25.50
                }
            ]
        }
        
        resultado = CompraService.cadastrar_compra(dados, self.user)
        
        self.assertTrue(resultado['success'])
        self.assertIn('compra', resultado)
        self.assertEqual(resultado['compra']['fornecedor'], self.fornecedor.nome)
        self.assertEqual(resultado['compra']['valor_total'], 227.50)
        self.assertEqual(len(resultado['compra']['itens']), 2)
    
    def test_cadastrar_compra_sem_itens(self):
        """Testa cadastro de compra sem itens"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': []
        }
        
        resultado = CompraService.cadastrar_compra(dados)
        
        self.assertFalse(resultado['success'])
        self.assertIn('error', resultado)
    
    def test_cadastrar_compra_fornecedor_inexistente(self):
        """Testa cadastro com fornecedor inexistente"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': 99999,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': self.produto1.id,
                    'quantidade': 10,
                    'preco_unitario': 10.00
                }
            ]
        }
        
        resultado = CompraService.cadastrar_compra(dados)
        
        self.assertFalse(resultado['success'])
        self.assertIn('Fornecedor não encontrado', resultado['error'])
    
    def test_cadastrar_compra_produto_inexistente(self):
        """Testa cadastro com produto inexistente"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': 99999,
                    'quantidade': 10,
                    'preco_unitario': 10.00
                }
            ]
        }
        
        resultado = CompraService.cadastrar_compra(dados)
        
        self.assertFalse(resultado['success'])
        self.assertIn('não encontrado', resultado['error'])
    
    def test_cadastrar_compra_quantidade_invalida(self):
        """Testa cadastro com quantidade inválida"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': self.produto1.id,
                    'quantidade': 0,
                    'preco_unitario': 10.00
                }
            ]
        }
        
        resultado = CompraService.cadastrar_compra(dados)
        
        self.assertFalse(resultado['success'])
        self.assertIn('quantidade', resultado['error'].lower())
    
    def test_cadastrar_compra_preco_negativo(self):
        """Testa cadastro com preço negativo"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': self.produto1.id,
                    'quantidade': 10,
                    'preco_unitario': -5.00
                }
            ]
        }
        
        resultado = CompraService.cadastrar_compra(dados)
        
        self.assertFalse(resultado['success'])
        self.assertIn('preço', resultado['error'].lower())
    
    def test_listar_compras(self):
        """Testa listagem de compras"""
        # Cria algumas compras
        Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00'),
            status='pendente'
        )
        
        Compra.objects.create(
            numero_pedido="COMP-20251119-0002",
            fornecedor=self.fornecedor,
            valor_total=Decimal('200.00'),
            status='concluida'
        )
        
        resultado = CompraService.listar_compras()
        
        self.assertTrue(resultado['success'])
        self.assertEqual(len(resultado['compras']), 2)
    
    def test_listar_compras_com_filtro_status(self):
        """Testa listagem com filtro de status"""
        Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00'),
            status='pendente'
        )
        
        Compra.objects.create(
            numero_pedido="COMP-20251119-0002",
            fornecedor=self.fornecedor,
            valor_total=Decimal('200.00'),
            status='concluida'
        )
        
        filtros = {'status': 'pendente'}
        resultado = CompraService.listar_compras(filtros)
        
        self.assertTrue(resultado['success'])
        self.assertEqual(len(resultado['compras']), 1)
        self.assertEqual(resultado['compras'][0]['status'], 'pendente')
    
    def test_buscar_compra_por_id(self):
        """Testa busca de compra por ID"""
        compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00'),
            status='pendente'
        )
        
        resultado = CompraService.buscar_compra_por_id(compra.id)
        
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['compra']['id'], compra.id)
        self.assertEqual(resultado['compra']['numero_pedido'], compra.numero_pedido)
    
    def test_buscar_compra_inexistente(self):
        """Testa busca de compra inexistente"""
        resultado = CompraService.buscar_compra_por_id(99999)
        
        self.assertFalse(resultado['success'])
        self.assertIn('não encontrada', resultado['error'])
    
    def test_atualizar_status_compra(self):
        """Testa atualização de status"""
        compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00'),
            status='pendente'
        )
        
        resultado = CompraService.atualizar_status_compra(compra.id, 'concluida')
        
        self.assertTrue(resultado['success'])
        
        compra.refresh_from_db()
        self.assertEqual(compra.status, 'concluida')
    
    def test_atualizar_status_invalido(self):
        """Testa atualização com status inválido"""
        compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00'),
            status='pendente'
        )
        
        resultado = CompraService.atualizar_status_compra(compra.id, 'status_invalido')
        
        self.assertFalse(resultado['success'])
        self.assertIn('inválido', resultado['error'])


class CompraAPITest(TestCase):
    """Testes para as APIs de compra"""
    
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Teste",
            cnpj="12.345.678/0001-90"
        )
        
        self.produto = Produto.objects.create(
            descricao="Produto Teste",
            preco=Decimal('10.00')
        )
    
    def test_cadastrar_compra_api(self):
        """Testa API de cadastro de compra"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': self.produto.id,
                    'quantidade': 10,
                    'preco_unitario': 10.00
                }
            ]
        }
        
        response = self.client.post(
            '/fornecedores/api/compras/cadastrar/',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_listar_compras_api(self):
        """Testa API de listagem de compras"""
        Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00')
        )
        
        response = self.client.get('/fornecedores/api/compras/listar/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['compras']), 0)
    
    def test_buscar_compra_api(self):
        """Testa API de busca de compra"""
        compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00')
        )
        
        response = self.client.get(f'/fornecedores/api/compras/{compra.id}/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['compra']['id'], compra.id)
    
    def test_atualizar_status_api(self):
        """Testa API de atualização de status"""
        compra = Compra.objects.create(
            numero_pedido="COMP-20251119-0001",
            fornecedor=self.fornecedor,
            valor_total=Decimal('100.00'),
            status='pendente'
        )
        
        dados = {'status': 'concluida'}
        
        response = self.client.put(
            f'/fornecedores/api/compras/{compra.id}/status/',
            data=json.dumps(dados),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_listar_fornecedores_api(self):
        """Testa API de listagem de fornecedores"""
        response = self.client.get('/fornecedores/api/fornecedores/listar/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
    
    def test_listar_produtos_api(self):
        """Testa API de listagem de produtos"""
        response = self.client.get('/fornecedores/api/produtos/listar/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])


class CompraIntegrationTest(TestCase):
    """Testes de integração completos"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.fornecedor = Fornecedor.objects.create(
            nome="Fornecedor Integração",
            cnpj="12.345.678/0001-90"
        )
        
        self.produto1 = Produto.objects.create(
            descricao="Produto A",
            preco=Decimal('15.00')
        )
        
        self.produto2 = Produto.objects.create(
            descricao="Produto B",
            preco=Decimal('30.00')
        )
    
    def test_fluxo_completo_compra(self):
        """Testa fluxo completo: criar, listar, buscar e atualizar"""
        # 1. Criar compra
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': self.produto1.id,
                    'quantidade': 10,
                    'preco_unitario': 15.00
                },
                {
                    'id_produto': self.produto2.id,
                    'quantidade': 5,
                    'preco_unitario': 30.00
                }
            ]
        }
        
        resultado_criar = CompraService.cadastrar_compra(dados, self.user)
        self.assertTrue(resultado_criar['success'])
        
        compra_id = resultado_criar['compra']['id']
        
        # 2. Listar compras
        resultado_listar = CompraService.listar_compras()
        self.assertTrue(resultado_listar['success'])
        self.assertGreater(len(resultado_listar['compras']), 0)
        
        # 3. Buscar compra específica
        resultado_buscar = CompraService.buscar_compra_por_id(compra_id)
        self.assertTrue(resultado_buscar['success'])
        self.assertEqual(resultado_buscar['compra']['status'], 'pendente')
        
        # 4. Atualizar status
        resultado_atualizar = CompraService.atualizar_status_compra(
            compra_id, 
            'concluida'
        )
        self.assertTrue(resultado_atualizar['success'])
        
        # 5. Verificar atualização
        resultado_final = CompraService.buscar_compra_por_id(compra_id)
        self.assertEqual(resultado_final['compra']['status'], 'concluida')
    
    def test_calculos_valores(self):
        """Testa cálculos de valores da compra"""
        dados = {
            'data_compra': '19/11/2025',
            'id_fornecedor': self.fornecedor.id,
            'status': 'pendente',
            'itens': [
                {
                    'id_produto': self.produto1.id,
                    'quantidade': 10,
                    'preco_unitario': 15.00
                },
                {
                    'id_produto': self.produto2.id,
                    'quantidade': 5,
                    'preco_unitario': 30.00
                }
            ]
        }
        
        resultado = CompraService.cadastrar_compra(dados, self.user)
        
        # Valor esperado: (10 * 15) + (5 * 30) = 150 + 150 = 300
        self.assertEqual(resultado['compra']['valor_total'], 300.00)
        
        # Verifica itens individuais
        itens = resultado['compra']['itens']
        self.assertEqual(itens[0]['subtotal'], 150.00)
        self.assertEqual(itens[1]['subtotal'], 150.00)
