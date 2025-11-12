from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Página de consulta
    path('consulta/', views.consulta_cliente, name='consulta_cliente'),
    
    # APIs
    path('api/listar/', views.listar_clientes, name='listar_clientes'),
    path('api/obter/<int:cliente_id>/', views.obter_cliente, name='obter_cliente'),
    path('api/criar/', views.criar_cliente, name='criar_cliente'),
    path('api/atualizar/<int:cliente_id>/', views.atualizar_cliente, name='atualizar_cliente'),
    path('api/deletar/<int:cliente_id>/', views.deletar_cliente, name='deletar_cliente'),
]