from django.db import models

# Create your models here.
class Funcionario(models.Model):
    id = models.BigAutoField(primary_key=True, null=False, auto_created=True)
    senha = models.CharField(max_length=255, null=False, blank=False)
    cargo = models.CharField(max_length=255, null=False, blank=False)
    nivel_acesso = models.PositiveBigIntegerField(null=False, blank=False)
    nome = models.CharField(max_length=255, null=False, blank=False)
    rg = models.CharField(max_length=255, null=False, blank=False)
    cpf = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(max_length=255, unique=True, null=False, blank=False)
    telefone = models.CharField(max_length=20, unique=True, null=False, blank=False)
    celular = models.CharField(max_length=255, null=False, blank=False)
    cep = models.PositiveIntegerField(null=False, blank=False)
    rua = models.CharField(max_length=255, null=False, blank=False)
    numero = models.PositiveBigIntegerField(null=False, blank=False)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    bairro = models.CharField(max_length=255, null=False, blank=False)
    cidade = models.CharField(max_length=255, null=False, blank=False)
    estado = models.CharField(max_length=255, null=False, blank=False)

