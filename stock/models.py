from django.db import models

# Create your models here.
class Stock(models.Model):
    code = models.CharField(unique=True, max_length=10)
    stock = models.CharField(max_length=30)
    market = models.CharField(max_length=30)
    industry = models.CharField(max_length=30)

    def __str__(self):
        return self.stock

    class Meta:
        db_table = 'Stock'
        verbose_name = '주식'
        verbose_name_plural = '주식'
