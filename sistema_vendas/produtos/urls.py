from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    # Página de consulta
    path('consulta/', views.consulta_produto, name='consulta_produto'),
    
    # Página de cadastro/edição
    path('cadastro/', views.cadastro_produto, name='cadastro_produto'),
    
    # APIs
    path('api/listar/', views.listar_produtos, name='listar_produtos'),
    path('api/obter/<int:produto_id>/', views.obter_produto, name='obter_produto'),
    path('api/criar/', views.criar_produto, name='criar_produto'),
    path('api/atualizar/<int:produto_id>/', views.atualizar_produto, name='atualizar_produto'),
    path('api/deletar/<int:produto_id>/', views.deletar_produto, name='deletar_produto'),
    path('api/fornecedores/', views.listar_fornecedores, name='listar_fornecedores'),
]