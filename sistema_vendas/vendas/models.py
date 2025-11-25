from django.db import models
from clientes.models import Cliente
from produtos.models import Produto

class Venda(models.Model):
    """
    Representa uma venda no sistema.
    Uma venda pode ter vários itens (relação 1:N com ItemVenda).
    """
    id = models.BigAutoField(primary_key=True)
    cliente_id = models.ForeignKey(
        Cliente, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        db_column='cliente_id_id'
    )
    data_venda = models.DateTimeField(null=False)
    total_venda = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    observacoes = models.TextField(blank=True, default='')
    
    class Meta:
        db_table = 'vendas_venda'
        managed = True  # IMPORTANTE: Django não vai tentar criar/alterar a tabela
        verbose_name = 'Venda'
        verbose_name_plural = 'Vendas'
    
    def __str__(self):
        return f"Venda {self.id} - R$ {self.total_venda}"


class ItemVenda(models.Model):
    """
    Representa um item dentro de uma venda.
    Cada item pertence a UMA venda (FK para Venda).
    """
    id = models.BigAutoField(primary_key=True)
    venda_id = models.ForeignKey(
        Venda, 
        on_delete=models.CASCADE, 
        null=False,
        related_name='itens',
        db_column='venda_id_id'
    )
    produto_id = models.ForeignKey(
        Produto, 
        on_delete=models.CASCADE, 
        null=False,
        db_column='produto_id_id'
    )
    quantidade = models.IntegerField(null=False, default=1)
    subTotal = models.DecimalField(
        null=False, 
        blank=False, 
        max_digits=10, 
        decimal_places=2,
        db_column='subTotal'
    )
    
    class Meta:
        db_table = 'vendas_itemvenda'
        managed = True  # IMPORTANTE: Django não vai tentar criar/alterar a tabela
        verbose_name = 'Item de Venda'
        verbose_name_plural = 'Itens de Venda'
    
    def __str__(self):
        return f"Item {self.id} - Venda {self.venda_id.id}"