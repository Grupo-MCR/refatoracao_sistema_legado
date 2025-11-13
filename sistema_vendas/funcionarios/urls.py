from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.CadastrarFuncionario, name="cadastrar"),
    #path('editar/', views.EditarFuncionario, name="editar"),
]