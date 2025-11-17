from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.CadastrarFuncionario, name="cadastrar"),
    path('editar/id=<int:id>', views.EditarFuncionario, name="editar"),
]