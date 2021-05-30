from django.db import models

# Create your models here.
class Stock(models.Model):
    stock = models.CharField(max_length=30)
    code = models.CharField(unique=True, max_length=10)

    def __str__(self):
        return self.stock

    class Meta:
        db_table = 'Stock'
        verbose_name = '주식'
        verbose_name_plural = '주식'
