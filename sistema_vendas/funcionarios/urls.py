from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.CadastrarFuncionario, name="cadastrar"),
    path('consultar/', views.ConsultarFuncionarios, name="consultar"),
    path('editar/id=<int:id>', views.EditarFuncionario, name="editar"),
]