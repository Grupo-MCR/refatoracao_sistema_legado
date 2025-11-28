from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from django.utils import timezone
import json

from clientes.models import Cliente
from produtos.models import Produto
from fornecedores.models import Fornecedor
from .models import Venda as VendaModel, ItemVenda


class PagamentosTestCase(TestCase):
    """Testes específicos para a tela de Pagamentos"""
    
    def setUp(self):
        """Configuração inicial"""
        self.client = Client()
        
        # Criar fornecedor
        self.fornecedor = Fornecedor.objects.create(
            nome='Fornecedor Teste',
            cnpj='12345678901234'
        )
        
        # Criar cliente
        self.cliente = Cliente.objects.create(
            nome='Maria Santos',
            cpf='98765432100',
            email='maria@teste.com'
        )
        
        # Criar produto
        self.produto = Produto.objects.create(
            descricao='Produto Teste',
            preco=Decimal('50.00'),
            qtd_estoque=100,
            fornecedor=self.fornecedor  # Corrigido
        )
    
    def criar_venda_teste(self, total=Decimal('100.00')):
        """Método auxiliar para criar uma venda"""
        venda = VendaModel.objects.create(
            cliente_id=self.cliente,
            data_venda=timezone.now(),
            total_venda=total,
            observacoes='Venda de teste'
        )
        
        ItemVenda.objects.create(
            venda_id=venda,
            produto_id=self.produto,
            quantidade=2,
            subTotal=total
        )
        
        return venda
    
    def test_acesso_tela_pagamento(self):
        """Testa o acesso à tela de pagamentos"""
        response = self.client.get(reverse('pagamentos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pagamento.html')
    
    def test_pagamento_dinheiro_valor_exato(self):
        """Testa pagamento em dinheiro com valor exato"""
        venda = self.criar_venda_teste(Decimal('100.00'))
        
        # Simula sessão
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 100.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': 'Pagamento em dinheiro'
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 0.0)
        self.assertIn('mensagem', result)
    
    def test_pagamento_dinheiro_com_troco(self):
        """Testa pagamento em dinheiro com troco"""
        venda = self.criar_venda_teste(Decimal('100.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 150.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 50.0)
    
    def test_pagamento_misto(self):
        """Testa pagamento com múltiplas formas (misto)"""
        venda = self.criar_venda_teste(Decimal('100.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 50.00,
            'cartao': 30.00,
            'cheque': 20.00,
            'observacoes': 'Pagamento misto'
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 0.0)
        
        # Verifica se as informações foram salvas
        venda_atualizada = VendaModel.objects.get(id=venda.id)
        self.assertIn('Dinheiro R$50', venda_atualizada.observacoes)
        self.assertIn('Cartão R$30', venda_atualizada.observacoes)
        self.assertIn('Cheque R$20', venda_atualizada.observacoes)
    
    def test_pagamento_cartao_valor_exato(self):
        """Testa pagamento apenas com cartão"""
        venda = self.criar_venda_teste(Decimal('75.50'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 0,
            'cartao': 75.50,
            'cheque': 0,
            'observacoes': 'Pagamento no cartão'
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 0.0)
    
    def test_pagamento_cheque(self):
        """Testa pagamento com cheque"""
        venda = self.criar_venda_teste(Decimal('200.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 0,
            'cartao': 0,
            'cheque': 200.00,
            'observacoes': 'Cheque número 123456'
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 0.0)
    
    def test_pagamento_valor_insuficiente(self):
        """Testa pagamento com valor menor que o total"""
        venda = self.criar_venda_teste(Decimal('100.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 50.00,
            'cartao': 25.00,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('erro', result)
        self.assertIn('menor que o total', result['erro'])
    
    def test_pagamento_valores_decimais(self):
        """Testa pagamento com valores decimais precisos"""
        venda = self.criar_venda_teste(Decimal('47.83'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 47.83,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 0.0)
    
    def test_pagamento_troco_centavos(self):
        """Testa cálculo de troco com centavos"""
        venda = self.criar_venda_teste(Decimal('19.47'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 20.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertAlmostEqual(result['troco'], 0.53, places=2)
    
    def test_pagamento_grande_quantidade_dinheiro(self):
        """Testa pagamento com valor grande"""
        venda = self.criar_venda_teste(Decimal('1234.56'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 1500.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertAlmostEqual(result['troco'], 265.44, places=2)
    
    def test_pagamento_com_observacoes_longas(self):
        """Testa pagamento com observações longas"""
        venda = self.criar_venda_teste(Decimal('50.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        observacao_longa = 'Cliente solicitou nota fiscal. ' * 20
        
        data = {
            'dinheiro': 50.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': observacao_longa
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        venda_atualizada = VendaModel.objects.get(id=venda.id)
        self.assertIn(observacao_longa[:50], venda_atualizada.observacoes)
    
    def test_pagamento_tres_formas_com_troco(self):
        """Testa pagamento com as 3 formas e troco"""
        venda = self.criar_venda_teste(Decimal('100.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 50.00,
            'cartao': 40.00,
            'cheque': 20.00,
            'observacoes': 'Pagamento completo'
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['troco'], 10.0)
    
    def test_limpeza_sessao_apos_pagamento(self):
        """Testa se a sessão é limpa após o pagamento"""
        venda = self.criar_venda_teste(Decimal('50.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        data = {
            'dinheiro': 50.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verifica se a sessão foi limpa
        session = self.client.session
        self.assertNotIn('venda_id', session)
    
    def test_pagamento_venda_inexistente(self):
        """Testa pagamento de venda que não existe"""
        session = self.client.session
        session['venda_id'] = 99999  # ID inexistente
        session.save()
        
        data = {
            'dinheiro': 100.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_tela_pagamento_exibe_info_venda(self):
        """Testa se a tela de pagamento exibe informações da venda"""
        venda = self.criar_venda_teste(Decimal('150.00'))
        
        session = self.client.session
        session['venda_id'] = venda.id
        session.save()
        
        response = self.client.get(reverse('pagamentos'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(venda.id))
        self.assertContains(response, '150.00')
    
    def test_multiplos_pagamentos_sequenciais(self):
        """Testa múltiplos pagamentos em sequência"""
        for i in range(3):
            venda = self.criar_venda_teste(Decimal('100.00'))
            
            session = self.client.session
            session['venda_id'] = venda.id
            session.save()
            
            data = {
                'dinheiro': 100.00,
                'cartao': 0,
                'cheque': 0,
                'observacoes': f'Venda {i+1}'
            }
            
            response = self.client.post(
                reverse('processar_pagamento'),
                data=json.dumps(data),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
        
        # Verifica se todas as vendas foram processadas
        vendas = VendaModel.objects.all()
        self.assertEqual(vendas.count(), 3)
    
    def test_pagamento_sem_venda_na_sessao(self):
        """Testa tentativa de pagamento sem venda na sessão"""
        data = {
            'dinheiro': 100.00,
            'cartao': 0,
            'cheque': 0,
            'observacoes': ''
        }
        
        response = self.client.post(
            reverse('processar_pagamento'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        result = response.json()
        self.assertIn('erro', result)
        self.assertIn('Nenhuma venda em andamento', result['erro'])


class CalculosPagamentosTestCase(TestCase):
    """Testes de cálculos de pagamentos"""
    
    def test_calculo_troco_simples(self):
        """Testa cálculo simples de troco"""
        total_venda = Decimal('50.00')
        pago = Decimal('100.00')
        troco_esperado = pago - total_venda
        self.assertEqual(troco_esperado, Decimal('50.00'))
    
    def test_calculo_troco_centavos(self):
        """Testa cálculo de troco com centavos"""
        total_venda = Decimal('47.83')
        pago = Decimal('50.00')
        troco_esperado = pago - total_venda
        self.assertEqual(troco_esperado, Decimal('2.17'))
    
    def test_soma_multiplas_formas_pagamento(self):
        """Testa soma de múltiplas formas de pagamento"""
        dinheiro = Decimal('25.50')
        cartao = Decimal('30.00')
        cheque = Decimal('20.25')
        total = dinheiro + cartao + cheque
        self.assertEqual(total, Decimal('75.75'))
    
    def test_precisao_decimal(self):
        """Testa precisão de cálculos decimais"""
        valor1 = Decimal('10.01')
        valor2 = Decimal('20.02')
        valor3 = Decimal('30.03')
        total = valor1 + valor2 + valor3
        self.assertEqual(total, Decimal('60.06'))
    
    def test_troco_zero(self):
        """Testa cálculo quando não há troco"""
        total_venda = Decimal('100.00')
        pago = Decimal('100.00')
        troco = pago - total_venda
        self.assertEqual(troco, Decimal('0.00'))
    
    def test_valores_grandes(self):
        """Testa cálculos com valores grandes"""
        total_venda = Decimal('9999.99')
        pago = Decimal('10000.00')
        troco = pago - total_venda
        self.assertEqual(troco, Decimal('0.01'))