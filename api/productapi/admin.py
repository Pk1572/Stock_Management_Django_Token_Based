from django.contrib import admin
from authapi.models import CustomUser
from .models import Product, ProductStock, History, Units


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'product_type', 'product_quantity', 'price', 'company')
    list_filter = ('company', 'product_type', 'is_active')
    search_fields = ('product_name', 'company__username')
    raw_id_fields = ('company',)


class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_quantity', 'transaction_type')  # Fixed product field name
    search_fields = ('product__product_name',)  # Correctly searching by product name


class HistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_quantity', 'transaction_type', 'updated_date')
    search_fields = ('product__product_name',)  # Correct related field lookup


class UnitsAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'company')
    search_fields = ('unit_name', 'company__username')


if not admin.site.is_registered(CustomUser):
    class CustomUserAdmin(admin.ModelAdmin):
        list_display = ('username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')

    admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductStock, ProductStockAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(Units, UnitsAdmin)
