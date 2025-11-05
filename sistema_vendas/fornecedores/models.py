from django.db import models

# Create your models here.

class Fornecedor(models.Model):
    nome = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=100)
    email = models.EmailField(max_length=200, blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    celular = models.CharField(max_length=30, blank=True, null=True)
    cep = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    numero = models.IntegerField(blank=True, null=True)
    complemento = models.CharField(max_length=200, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)

    def __str__(self):
        return self.nome

    class Meta:
        db_table = 'tb_fornecedores'
