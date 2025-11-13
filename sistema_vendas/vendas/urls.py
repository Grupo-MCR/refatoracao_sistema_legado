from django.urls import path
from . import views

urlpatterns = [
    path('', views.Venda, name='ponto_venda'),
]
