from django.urls import path
from . import views

urlpatterns = [
    path('cadastrar/', views.CadastrarFuncionario, name='Cadastro'),
]