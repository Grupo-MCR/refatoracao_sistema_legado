from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.cadastrar_funcionario, name='cadastroFornecedor'),
    path('consultar/', views.consulta_fornecedor, name='consultaFornecedor'),
    path('editar/', views.editar_fornecedor, name='editarFornecedor'),
]