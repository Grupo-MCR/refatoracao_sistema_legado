from django.urls import path
from . import views

urlpatterns = [
    # Cadastro de fornecedor
    path('cadastrar/', views.cadastrar_fornecedor, name='cadastroFornecedor'),
    
    # Listagem/Consulta de fornecedores
    path('consultar/', views.consulta_fornecedor, name='consultaFornecedor'),
    
    # Edição de fornecedor (agora recebe o ID)
    path('editar/id=<int:fornecedor_id>', views.editar_fornecedor, name='editarFornecedor'),
    
    # Exclusão de fornecedor (opcional)
    path('excluir/id=<int:fornecedor_id>', views.excluir_fornecedor, name='excluirFornecedor'),
]


