from django.db import models

# Create your models here.
class Venda(models.Model):
  id = models.BigAutoField(primary_key = True, null = False, unique = True)
  cliente_id = models.ForeignKey(Cliente, on_delete=models.CASCADE, null = False,)
  itemVenda_id = models.ForeignKey(ItemVenda, on_delete=models.CASCADE, null = False,)
  data_venda = models.DateTimeField(null = False,)
  total_venda = models.DecimalField(null = False,)
  observacoes = models.CharField(max_length=255)

class ItemVenda(models.Model):
  id = models.BigAutoField(primary_key = True, null = False, unique = True)
  produto_id = models.ForeignKey(Produto, on_delete=models.CASCADE, null = False,)
  quantidade = models.IntegerField
  subTotal = models.DecimalField(null = False)
    
