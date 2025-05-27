import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import Product, InventoryMovement, CurrentStock
from django.db.models import Sum, Case, When, F, Q
from django.utils import timezone

def get_threshold_for_product(product):
    """Determina el umbral de stock bajo basado en el precio del producto"""
    if product.sale_price <= 10:  # Productos pequeños/baratos
        return 50
    elif product.sale_price <= 100:  # Productos medianos
        return 15
    elif product.sale_price <= 500:  # Productos grandes
        return 5
    else:  # Productos premium
        return 3

def calculate_stock():
    print("Iniciando cálculo de stock actual...")
    
    # Obtener todos los productos
    products = Product.objects.filter(active=True)
    
    for product in products:
        try:
            # Calcular movimientos netos
            movements = InventoryMovement.objects.filter(product=product)
            
            inbound_total = movements.filter(
                movement_type='INBOUND'
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            outbound_total = movements.filter(
                movement_type__in=['OUTBOUND', 'ADJUSTMENT_OUT']
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0
            
            # Calcular stock actual
            current_quantity = inbound_total - outbound_total
            
            # Calcular costo total del inventario
            total_cost = Decimal(current_quantity) * product.cost
            
            # Obtener el umbral específico para este producto
            threshold = get_threshold_for_product(product)
            
            # Determinar el estado del stock
            stock_status = 'CRITICAL' if current_quantity <= threshold else 'OK'
            if current_quantity <= 0:
                stock_status = 'OUT_OF_STOCK'
            
            # Actualizar o crear registro de stock actual
            current_stock, created = CurrentStock.objects.update_or_create(
                product=product,
                defaults={
                    'quantity': current_quantity,
                    'total_inventory_cost': total_cost,
                    'last_updated': timezone.now(),
                    'stock_status': stock_status,
                    'threshold': threshold
                }
            )
            
            status = "creado" if created else "actualizado"
            print(f"✓ Stock {status} para {product.product_name}:")
            print(f"  - Cantidad actual: {current_quantity}")
            print(f"  - Umbral: {threshold}")
            print(f"  - Estado: {stock_status}")
            print(f"  - Costo total: ${total_cost:,.2f}")
            print(f"  - Entradas totales: {inbound_total}")
            print(f"  - Salidas totales: {outbound_total}")
            
        except Exception as e:
            print(f"✗ Error procesando {product.product_name}: {str(e)}")

if __name__ == "__main__":
    print("=== Actualización de Stock ===")
    calculate_stock()
    print("\nProceso completado.")
    
    # Mostrar resumen
    print("\nResumen de stock:")
    critical_stock = CurrentStock.objects.filter(
        Q(stock_status='CRITICAL') | Q(stock_status='OUT_OF_STOCK')
    ).select_related('product')
    
    total_value = sum(stock.total_inventory_cost for stock in CurrentStock.objects.all())
    
    print(f"\nValor total del inventario: ${total_value:,.2f}")
    print(f"Productos en estado crítico: {critical_stock.count()}")
    
    if critical_stock:
        print("\nProductos que requieren atención:")
        for stock in critical_stock:
            print(f"- {stock.product.product_name}: {stock.quantity}/{stock.threshold} unidades ({stock.stock_status})") 