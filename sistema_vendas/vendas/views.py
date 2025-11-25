from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
import json
import traceback

from clientes.models import Cliente
from produtos.models import Produto
from .models import Venda as VendaModel, ItemVenda

# Create your views here.
def Venda_View(request):
    """Renderiza a tela do Ponto de Vendas"""
    template = loader.get_template('ponto_vendas.html')
    return HttpResponse(template.render({}, request))

def Pagamento(request):
    """Renderiza a tela de Pagamentos"""
    # Recupera os dados da venda da sessão
    venda_id = request.session.get('venda_id')
    venda_data = None
    
    print(f"[DEBUG] Acessando tela de pagamentos - venda_id na sessão: {venda_id}")
    
    if venda_id:
        try:
            venda = VendaModel.objects.get(id=venda_id)
            cliente_nome = venda.cliente_id.nome if venda.cliente_id else 'Cliente não identificado'
            
            venda_data = {
                'id': venda.id,
                'total': float(venda.total_venda),
                'cliente': cliente_nome
            }
            
            print(f"[DEBUG] Venda encontrada: ID={venda.id}, Cliente={cliente_nome}, Total={venda.total_venda}")
            
        except VendaModel.DoesNotExist:
            print(f"[ERRO] Venda não encontrada para ID: {venda_id}")
    else:
        print(f"[DEBUG] Nenhuma venda_id na sessão")
    
    template = loader.get_template('pagamento.html')
    context = {'venda': venda_data}
    return HttpResponse(template.render(context, request))

def historico_vendas(request):
    """Renderiza a página de histórico de vendas"""
    template = loader.get_template('historico_vendas.html')
    return HttpResponse(template.render({}, request))

def buscar_cliente(request):
    """Busca cliente por CPF"""
    try:
        cpf = request.GET.get('cpf', '').strip()
        
        print(f"[DEBUG] Buscando cliente - CPF recebido: '{cpf}'")
        
        if not cpf:
            return JsonResponse({'erro': 'CPF não informado'}, status=400)
        
        # Remove caracteres especiais do CPF
        cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
        print(f"[DEBUG] CPF limpo: '{cpf_limpo}'")
        
        # Tenta buscar o cliente
        clientes = Cliente.objects.all()
        print(f"[DEBUG] Total de clientes no banco: {clientes.count()}")
        
        # Mostra os primeiros 3 clientes para debug
        for c in clientes[:3]:
            cpf_banco_limpo = c.cpf.replace('.', '').replace('-', '').replace(' ', '')
            print(f"[DEBUG] Cliente exemplo - ID: {c.id}, Nome: {c.nome}, CPF banco: '{c.cpf}', CPF limpo: '{cpf_banco_limpo}'")
        
        # CORREÇÃO: Busca comparando CPFs SEM formatação
        cliente = None
        for c in Cliente.objects.all():
            cpf_banco_limpo = c.cpf.replace('.', '').replace('-', '').replace(' ', '')
            if cpf_banco_limpo == cpf_limpo:
                cliente = c
                break
        
        if cliente:
            print(f"[DEBUG] Cliente encontrado: {cliente.nome}")
            return JsonResponse({
                'id': cliente.id,
                'nome': cliente.nome,
                'cpf': cliente.cpf,
                'email': cliente.email or '',
                'telefone': cliente.telefone or ''
            })
        else:
            print(f"[DEBUG] Cliente NÃO encontrado para CPF: {cpf_limpo}")
            return JsonResponse({'erro': 'Cliente não encontrado'}, status=404)
            
    except Exception as e:
        print(f"[ERRO] Erro ao buscar cliente: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'erro': f'Erro no servidor: {str(e)}'}, status=500)

def buscar_produto(request):
    """Busca produto por código (ID)"""
    try:
        codigo = request.GET.get('codigo', '').strip()
        
        print(f"[DEBUG] Buscando produto - Código recebido: '{codigo}'")
        
        if not codigo:
            return JsonResponse({'erro': 'Código não informado'}, status=400)
        
        # Verifica se é um número válido
        try:
            codigo_int = int(codigo)
        except ValueError:
            print(f"[DEBUG] Código inválido (não é número): '{codigo}'")
            return JsonResponse({'erro': 'Código deve ser um número'}, status=400)
        
        # Tenta buscar o produto
        produtos = Produto.objects.all()
        print(f"[DEBUG] Total de produtos no banco: {produtos.count()}")
        
        # Mostra os primeiros 3 produtos para debug
        for p in produtos[:3]:
            print(f"[DEBUG] Produto exemplo - ID: {p.id}, Desc: {p.descricao}, Estoque: {p.qtd_estoque}")
        
        # Busca o produto
        produto = Produto.objects.filter(id=codigo_int).first()
        
        if produto:
            print(f"[DEBUG] Produto encontrado: {produto.descricao}, Estoque: {produto.qtd_estoque}")
            return JsonResponse({
                'id': produto.id,
                'descricao': produto.descricao,
                'preco': float(produto.preco),
                'qtd_estoque': produto.qtd_estoque
            })
        else:
            print(f"[DEBUG] Produto NÃO encontrado para código: {codigo_int}")
            return JsonResponse({'erro': 'Produto não encontrado'}, status=404)
            
    except Exception as e:
        print(f"[ERRO] Erro ao buscar produto: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'erro': f'Erro no servidor: {str(e)}'}, status=500)

@csrf_exempt
def finalizar_venda(request):
    """Finaliza a venda e cria os registros no banco"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        cpf = data.get('cpf', '').strip()
        itens = data.get('itens', [])
        total = Decimal(str(data.get('total', 0)))
        observacoes = data.get('observacoes', '')
        
        print(f"[DEBUG] Finalizando venda - Total: {total}, Itens: {len(itens)}")
        
        if not itens:
            return JsonResponse({'erro': 'Nenhum item na venda'}, status=400)
        
        # Busca o cliente (opcional)
        cliente = None
        if cpf:
            cpf_limpo = cpf.replace('.', '').replace('-', '').replace(' ', '')
            cliente = Cliente.objects.filter(cpf=cpf_limpo).first()
            if cliente:
                print(f"[DEBUG] Venda para cliente: {cliente.nome}")
        
        # IMPORTANTE: Valida estoque ANTES de criar a venda
        print(f"[DEBUG] Validando estoque dos itens...")
        for item in itens:
            codigo = item['codigo']
            quantidade_desejada = item['quantidade']
            
            try:
                produto = Produto.objects.get(id=codigo)
                print(f"[DEBUG] Item: {produto.descricao}")
                print(f"[DEBUG]   - Quantidade desejada: {quantidade_desejada}")
                print(f"[DEBUG]   - Estoque atual: {produto.qtd_estoque}")
                
                if produto.qtd_estoque < quantidade_desejada:
                    erro_msg = f'Estoque insuficiente para {produto.descricao}. Disponível: {produto.qtd_estoque}, Solicitado: {quantidade_desejada}'
                    print(f"[ERRO] {erro_msg}")
                    return JsonResponse({'erro': erro_msg}, status=400)
                    
            except Produto.DoesNotExist:
                return JsonResponse({'erro': f'Produto código {codigo} não encontrado'}, status=404)
        
        print(f"[DEBUG] Todos os itens têm estoque disponível. Criando venda...")
        
        # Cria a venda
        venda = VendaModel.objects.create(
            cliente_id=cliente,
            data_venda=timezone.now(),
            total_venda=total,
            observacoes=observacoes
        )
        
        print(f"[DEBUG] Venda criada com ID: {venda.id}")
        
        # Cria os itens da venda e atualiza estoque
        for item in itens:
            produto = Produto.objects.get(id=item['codigo'])
            
            # Cria o item
            item_venda = ItemVenda.objects.create(
                venda_id=venda,
                produto_id=produto,
                quantidade=item['quantidade'],
                subTotal=Decimal(str(item['subtotal']))
            )
            
            print(f"[DEBUG] Item criado: {produto.descricao} x {item['quantidade']}")
            
            # Atualiza o estoque
            estoque_anterior = produto.qtd_estoque
            produto.qtd_estoque -= item['quantidade']
            produto.save()
            
            print(f"[DEBUG] Estoque atualizado: {estoque_anterior} -> {produto.qtd_estoque}")
        
        # Salva o ID da venda na sessão para a tela de pagamento
        request.session['venda_id'] = venda.id
        
        print(f"[DEBUG] Venda finalizada com sucesso! ID: {venda.id}")
        
        return JsonResponse({
            'mensagem': 'Venda finalizada com sucesso!',
            'venda_id': venda.id,
            'total': float(venda.total_venda)
        })
        
    except Produto.DoesNotExist as e:
        print(f"[ERRO] Produto não encontrado: {str(e)}")
        return JsonResponse({'erro': 'Produto não encontrado'}, status=404)
    except Exception as e:
        print(f"[ERRO] Erro ao finalizar venda: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'erro': f'Erro no servidor: {str(e)}'}, status=500)

@csrf_exempt
def processar_pagamento(request):
    """Processa o pagamento da venda"""
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        venda_id = request.session.get('venda_id')
        
        print(f"[DEBUG] Processando pagamento - Venda ID: {venda_id}")
        
        if not venda_id:
            return JsonResponse({'erro': 'Nenhuma venda em andamento'}, status=400)
        
        venda = VendaModel.objects.get(id=venda_id)
        
        # Extrai os valores de pagamento
        dinheiro = Decimal(str(data.get('dinheiro', 0)))
        cartao = Decimal(str(data.get('cartao', 0)))
        cheque = Decimal(str(data.get('cheque', 0)))
        observacoes = data.get('observacoes', '')
        
        total_pago = dinheiro + cartao + cheque
        total_venda = venda.total_venda
        
        print(f"[DEBUG] Total venda: {total_venda}, Total pago: {total_pago}")
        
        # Calcula o troco
        troco = total_pago - total_venda
        
        if total_pago < total_venda:
            return JsonResponse({
                'erro': 'Valor pago é menor que o total da venda'
            }, status=400)
        
        # Atualiza as observações da venda com informações de pagamento
        info_pagamento = f" \nPagamento:"
        if(dinheiro > 0):
            info_pagamento = info_pagamento + f" Dinheiro R${dinheiro}";
        
        if(cartao > 0):
            info_pagamento = info_pagamento + f" Cartão R${cartao}"
        
        if(cheque > 0):
            info_pagamento = info_pagamento + f" Cheque R${cheque}"
        
        if observacoes:
            info_pagamento = f"{observacoes}; {info_pagamento}"
        
        venda.observacoes = info_pagamento
        venda.save()
        
        print(f"[DEBUG] Pagamento processado. Troco: {troco}")
        
        # Limpa a sessão
        del request.session['venda_id']
        
        return JsonResponse({
            'mensagem': 'Pagamento processado com sucesso!',
            'troco': float(troco),
            'venda_id': venda.id
        })
        
    except VendaModel.DoesNotExist:
        print(f"[ERRO] Venda não encontrada: {venda_id}")
        return JsonResponse({'erro': 'Venda não encontrada'}, status=404)
    except Exception as e:
        print(f"[ERRO] Erro ao processar pagamento: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'erro': f'Erro no servidor: {str(e)}'}, status=500)


# ============================================
# NOVAS VIEWS PARA HISTÓRICO DE VENDAS
# ============================================

@csrf_exempt
@require_http_methods(["POST"])
def buscar_vendas_periodo(request):
    """
    Busca vendas em um período específico
    Espera JSON: {"dataInicio": "DD/MM/YYYY", "dataFim": "DD/MM/YYYY"}
    Retorna: lista de vendas
    """
    try:
        data = json.loads(request.body)
        print(data)
        data_inicio = data.get('dataInicio')
        data_fim = data.get('dataFim')
        
        print(f"[DEBUG] Buscando vendas - Período: {data_inicio} até {data_fim}")
        
        # Converter datas de DD/MM/YYYY para objeto datetime
        data_inicio_obj = datetime.strptime(data_inicio, '%d/%m/%Y')
        data_fim_obj = datetime.strptime(data_fim, '%d/%m/%Y')
        
        # Buscar vendas no período
        vendas = VendaModel.objects.filter(
            data_venda__date__gte=data_inicio_obj.date(),
            data_venda__date__lte=data_fim_obj.date()
        ).select_related('cliente_id').order_by('-data_venda')
        
        print(f"[DEBUG] Vendas encontradas: {vendas.count()}")
        
        # Formatar dados para retorno
        vendas_list = []
        for venda in vendas:
            vendas_list.append({
                'codigo': str(venda.id).zfill(6),  # Formata ID como código com zeros à esquerda
                'data': venda.data_venda.strftime('%d/%m/%Y'),
                'cliente': venda.cliente_id.nome if venda.cliente_id else 'Cliente não identificado',
                'total': f'R$ {float(venda.total_venda):.2f}'.replace('.', ','),
                'obs': venda.observacoes[:50] if venda.observacoes else ''  # Limita observações a 50 caracteres
            })
        
        return JsonResponse({
            'success': True,
            'vendas': vendas_list
        })
        
    except ValueError as e:
        print(f"[ERRO] Data inválida: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Data inválida. Use o formato DD/MM/YYYY'
        }, status=400)
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar vendas: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Erro no servidor: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def buscar_total_vendas_data(request):
    """
    Busca o total de vendas em uma data específica
    Espera JSON: {"data": "DD/MM/YYYY"}
    Retorna: total de vendas
    """
    try:
        data = json.loads(request.body)
        data_venda = data.get('data')
        
        print(f"[DEBUG] Buscando total de vendas - Data: {data_venda}")
        
        # Converter data de DD/MM/YYYY para objeto datetime
        data_venda_obj = datetime.strptime(data_venda, '%d/%m/%Y')
        
        # Buscar total de vendas na data
        total = VendaModel.objects.filter(
            data_venda__date=data_venda_obj.date()
        ).aggregate(total=Sum('total_venda'))['total'] or Decimal('0')
        
        print(f"[DEBUG] Total encontrado: R$ {total}")
        
        return JsonResponse({
            'success': True,
            'total': f'R$ {float(total):.2f}'.replace('.', ','),
            'data': data_venda
        })
        
    except ValueError as e:
        print(f"[ERRO] Data inválida: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Data inválida. Use o formato DD/MM/YYYY'
        }, status=400)
        
    except Exception as e:
        print(f"[ERRO] Erro ao buscar total: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f'Erro no servidor: {str(e)}'
        }, status=500)
