from django.urls import path
from . import views

urlpatterns = [
    # Tela do Ponto de Vendas
    path('ponto_venda/', views.Venda_View, name='ponto_venda'),
    
    # Tela de Pagamentos
    path('pagamentos/', views.Pagamento, name='pagamentos'),
    
    # APIs de busca
    path('buscar_cliente/', views.buscar_cliente, name='buscar_cliente'),
    path('buscar_produto/', views.buscar_produto, name='buscar_produto'),
    
    # APIs de processamento
    path('finalizar_venda/', views.finalizar_venda, name='finalizar_venda'),
    path('processar_pagamento/', views.processar_pagamento, name='processar_pagamento'),
]