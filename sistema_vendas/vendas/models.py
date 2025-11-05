from django.db import models
from clientes import models as c_models
from produtos import models as p_models

# Create your models here.
class ItemVenda(models.Model):
  id = models.BigAutoField(primary_key = True, null = False, unique = True)
  produto_id = models.ForeignKey(p_models.Produto, on_delete=models.CASCADE, null = False,)
  quantidade = models.IntegerField
  subTotal = models.DecimalField(null = False, blank= False, max_digits= 10, decimal_places= 2)

class Venda(models.Model):
  id = models.BigAutoField(primary_key = True, null = False, unique = True)
  cliente_id = models.ForeignKey(c_models.Cliente, on_delete=models.CASCADE, null = False,)
  itemVenda_id = models.ForeignKey(ItemVenda, on_delete=models.CASCADE, null = False,)
  data_venda = models.DateTimeField(null = False, )
  total_venda = models.DecimalField(null = False, blank= False, max_digits=10, decimal_places= 2)
  observacoes = models.CharField(max_length=255)


    
