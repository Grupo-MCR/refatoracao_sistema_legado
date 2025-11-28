from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    # Páginas
    path('consulta_produto/', views.consulta_produto, name='consulta_produto'),
    path('cadastro/', views.cadastro_produto, name='cadastro_produto'),
    path('relatorio/', views.relatorio_produtos, name='relatorio_produtos'),  
    
    # APIs
    path('api/listar/', views.listar_produtos, name='listar_produtos'),
    path('api/obter/<int:produto_id>/', views.obter_produto, name='obter_produto'),
    path('api/criar/', views.criar_produto, name='criar_produto'),
    path('api/atualizar/<int:produto_id>/', views.atualizar_produto, name='atualizar_produto'),
    path('api/deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    path('api/fornecedores/', views.listar_fornecedores, name='listar_fornecedores'),
    path('api/relatorio/', views.relatorio_produtos_vendidos, name='relatorio_produtos_vendidos'),  
]