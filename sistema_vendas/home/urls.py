from django.urls import path
from . import views

urlpatterns = [
    path('', views.Login, name='LoginPage'),
    path('login/', views.Login, name='Login')
]