from django.db import models
from fornecedores import models as f_models

class Produto(models.Model):
    """
    Model que representa um Produto
    """
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço")
    qtd_estoque = models.IntegerField(default=0, verbose_name="Quantidade em Estoque")
    fornecedor = models.ForeignKey(
        f_models.Fornecedor,
        on_delete=models.PROTECT,
        related_name='produtos',
        verbose_name="Fornecedor"
    )
    
    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['descricao']
    
    def __str__(self):
        return self.descricao