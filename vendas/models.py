from django.db import models

class Venda(models.Model):
    data = models.DateField()
    produto = models.CharField(max_length=100)
    quantidade_vendida = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.preco_total = self.quantidade_vendida * self.preco_unitario
        super().save(*args, **kwargs)