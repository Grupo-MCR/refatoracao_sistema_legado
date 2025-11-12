from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

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


class Compra(models.Model):
    """
    Model para registrar compras de fornecedores.
    """
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]

    numero_pedido = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número único do pedido de compra"
    )
    
    fornecedor = models.ForeignKey(
        'fornecedores.Fornecedor',
        on_delete=models.PROTECT,
        related_name='compras',
        help_text="Fornecedor da compra"
    )
    
    data_compra = models.DateTimeField(
        default=timezone.now,
        help_text="Data e hora da compra"
    )
    
    data_entrega_prevista = models.DateField(
        null=True,
        blank=True,
        help_text="Data prevista para entrega"
    )
    
    data_entrega_realizada = models.DateField(
        null=True,
        blank=True,
        help_text="Data real da entrega"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pendente',
        help_text="Status atual da compra"
    )
    
    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Valor total da compra"
    )
    
    valor_frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Valor do frete"
    )
    
    valor_desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Valor de desconto aplicado"
    )
    
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações adicionais sobre a compra"
    )
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    criado_por = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras_criadas',
        help_text="Usuário que criou a compra"
    )

    class Meta:
        db_table = 'compras'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-data_compra']

    def __str__(self):
        return f"Compra #{self.numero_pedido} - {self.fornecedor}"
      
