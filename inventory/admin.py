from django.contrib import admin
from .models import Product, InventoryMovement, CurrentStock, PredictorStock

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'category', 'cost', 'sale_price', 'active')
    list_filter = ('category', 'active')
    search_fields = ('product_id', 'product_name', 'sku')

@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('movement_id', 'date', 'product', 'movement_type', 'quantity', 'order_id')
    list_filter = ('movement_type', 'date')
    search_fields = ('movement_id', 'order_id', 'product__product_name')

@admin.register(CurrentStock)
class CurrentStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'last_updated', 'total_inventory_cost')
    search_fields = ('product__product_name',)

@admin.register(PredictorStock)
class PredictorStockAdmin(admin.ModelAdmin):
    list_display = ('date', 'product', 'units_sold', 'avg_sale_price', 'promotion_active', 'special_event')
    list_filter = ('date', 'promotion_active')
    search_fields = ('product__product_name', 'special_event')
