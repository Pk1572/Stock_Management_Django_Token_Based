from django.db import models
from authapi.models import Company

class Units(models.Model):
    unit_name = models.CharField(max_length=500, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="units")

    def __str__(self):
        return f'{self.unit_name} ({self.company.company_name})'


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=50)
    product_quantity = models.FloatField(default=0)
    unit = models.ForeignKey(Units, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=4, choices=[('sell', 'Sell'), ('buy', 'Buy')], default='buy')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='products')

    def __str__(self):
        return f'{self.product_name} ({self.company.company_name})'


class ProductStock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    product_quantity = models.FloatField(default=0)
    updated_date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=[('sell', 'Sell'), ('buy', 'Buy')])
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name="product_stocks")

    def __str__(self):
        return f'{self.product.product_name} - {self.product_quantity}'


class History(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="history")
    product_quantity = models.FloatField(default=0)
    transaction_type = models.CharField(
        max_length=10, choices=[('sell', 'Sell'), ('buy', 'Buy')]
    )
    updated_date = models.DateTimeField(auto_now_add=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="histories")

    def __str__(self):
        return f'{self.product.product_name} - {self.product_quantity}'

