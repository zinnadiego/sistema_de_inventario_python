import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import Product, InventoryMovement, CurrentStock

def generate_critical_movements():
    # Seleccionar algunos productos para ponerlos en estado crítico
    products = Product.objects.all()
    critical_products = random.sample(list(products), 3)  # 3 productos aleatorios
    
    for product in critical_products:
        # Obtener stock actual
        current_stock = CurrentStock.objects.get(product=product)
        
        # Calcular cuánto necesitamos vender para llegar al umbral
        threshold = current_stock.threshold
        target_quantity = threshold - 2  # 2 unidades por debajo del umbral
        units_to_sell = current_stock.quantity - target_quantity
        
        if units_to_sell > 0:
            # Crear varios movimientos de salida para llegar al nivel crítico
            num_movements = random.randint(2, 4)
            units_per_movement = units_to_sell // num_movements
            
            for i in range(num_movements):
                # El último movimiento ajusta la diferencia
                if i == num_movements - 1:
                    quantity = units_to_sell - (units_per_movement * (num_movements - 1))
                else:
                    quantity = units_per_movement
                
                if quantity > 0:
                    movement_id = f"MC{i+1:03d}{product.product_id[-4:]}"
                    
                    try:
                        InventoryMovement.objects.create(
                            movement_id=movement_id,
                            date=timezone.now() - timedelta(hours=random.randint(1, 4)),
                            product=product,
                            movement_type='OUTBOUND',
                            quantity=quantity,
                            order_id=f"CRIT{random.randint(1000, 9999)}",
                            notes=f"Movimiento para generar stock crítico"
                        )
                        print(f"✓ Creado movimiento de salida para {product.product_name}: {quantity} unidades")
                    except Exception as e:
                        print(f"✗ Error al crear movimiento {movement_id}: {str(e)}")

if __name__ == "__main__":
    print("Generando movimientos para stock crítico...")
    generate_critical_movements()
    print("\nProceso completado.") 