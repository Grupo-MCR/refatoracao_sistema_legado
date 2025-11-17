from django.urls import path
from . import views

urlpatterns = [
    path('ponto_venda/', views.Venda, name='ponto_venda'),
    path('pagamentos/', views.Pagamento, name='pagamentos'),
]
