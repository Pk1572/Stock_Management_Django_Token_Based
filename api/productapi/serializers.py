from rest_framework import serializers
from .models import Product, Units, ProductStock, History

class ProductSerializer(serializers.ModelSerializer):
    company = serializers.ReadOnlyField(source='company.company_name')
    unit_name = serializers.ReadOnlyField(source='unit.unit_name')

    class Meta:
        model = Product
        fields = [
            'product_id', 'product_name', 'product_type', 'product_quantity',
            'unit', 'unit_name', 'transaction_type', 'price', 'is_active',
            'company', 'created_at'
        ]
        read_only_fields = ['product_id', 'created_at', 'company']


class ProductStockSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductStock
        fields = ['product', 'product_quantity', 'updated_date', 'transaction_type', 'company']



class HistorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = History
        fields = ['id', 'product', 'product_name', 'product_quantity', 'transaction_type', 'updated_date', 'company']


class UnitSerializer(serializers.ModelSerializer):
    company = serializers.ReadOnlyField(source='company.company_name')

    class Meta:
        model = Units
        fields = ['id', 'unit_name', 'company']
