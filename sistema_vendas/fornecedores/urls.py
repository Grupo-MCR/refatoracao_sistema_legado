from django.urls import path
from . import views

app_name = 'fornecedores'

urlpatterns = [
    # Cadastro de fornecedor
    path('cadastrar/', views.cadastrar_fornecedor, name='cadastroFornecedor'),
    
    # Listagem/Consulta de fornecedores
    path('consultar/', views.consulta_fornecedor, name='consultaFornecedor'),
    
    # Edição de fornecedor (agora recebe o ID)
    path('editar/id=<int:fornecedor_id>', views.editar_fornecedor, name='editarFornecedor'),
    
    # Exclusão de fornecedor (opcional)
    path('excluir/id=<int:fornecedor_id>', views.excluir_fornecedor, name='excluirFornecedor'),
    
    # Cadastro de compra
    path('compra/', views.compra_fornecedor, name='compraFornecedor'),
    path('historico/<int:fornecedor_id>/', views.historico_compras_fornecedor, name='historicoComprasFornecedor'),
    
    # ==================== ROTAS DE API (JSON) ====================
    
    # APIs de Compras
    path('api/compras/cadastrar/', views.cadastrar_compra_api, name='api_cadastrar_compra'),
    path('api/compras/listar/', views.listar_compras_api, name='api_listar_compras'),
    path('api/compras/<int:compra_id>/', views.buscar_compra_api, name='api_buscar_compra'),
    path('api/compras/<int:compra_id>/status/', views.atualizar_status_compra_api, name='api_atualizar_status_compra'),
    
    # APIs Auxiliares
    path('api/fornecedores/listar/', views.listar_fornecedores_api, name='api_listar_fornecedores'),
    path('api/produtos/listar/', views.listar_produtos_api, name='api_listar_produtos'),
]
