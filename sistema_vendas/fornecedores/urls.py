from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.CadastrarFuncionario, name='Cadastro'),
    path('consultar/', views.home_fornecedor, name='homeFornecedor'),
    path('editar/', views.editar_fornecedor, name='editarFornecedor'),
]