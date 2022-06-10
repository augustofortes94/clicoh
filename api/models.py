from django.db import models
from django.utils import timezone


class Order(models.Model):
    date_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.date_time = timezone.now()
        return super(Order, self).save(*args, **kwargs)


class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return self.name


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True)
    cuantity = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
