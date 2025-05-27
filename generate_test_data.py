import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import Product, InventoryMovement, CurrentStock

def generate_movement_data(product, num_days=30):
    # Generar movimientos para los últimos num_days días
    end_date = timezone.now()
    start_date = end_date - timedelta(days=num_days)
    movement_counter = 1
    
    # Ajustar cantidades según el tipo de producto y su precio
    if product.sale_price <= 10:  # Productos pequeños/baratos (como cables)
        inbound_min, inbound_max = 50, 100
        outbound_min, outbound_max = 20, 40
    elif product.sale_price <= 100:  # Productos medianos (como mouse, teclados)
        inbound_min, inbound_max = 20, 40
        outbound_min, outbound_max = 10, 20
    elif product.sale_price <= 500:  # Productos grandes (como monitores)
        inbound_min, inbound_max = 10, 20
        outbound_min, outbound_max = 5, 10
    else:  # Productos premium (como laptops)
        inbound_min, inbound_max = 5, 10
        outbound_min, outbound_max = 2, 5
    
    # Generar al menos algunos movimientos para hoy
    today = timezone.now()
    for _ in range(3):  # 3 movimientos garantizados para hoy
        # Más probabilidad de entradas hoy para recuperar stock
        movement_type = random.choice(['INBOUND'] * 3 + ['OUTBOUND'])
        if movement_type == 'INBOUND':
            quantity = random.randint(inbound_min, inbound_max)
        else:
            quantity = random.randint(outbound_min, outbound_max)
        
        movement_id = f"M{movement_counter:04d}{product.product_id[-4:]}"
        movement_counter += 1
        
        InventoryMovement.objects.create(
            movement_id=movement_id,
            date=today - timedelta(hours=random.randint(0, 8)),  # Distribuir en las últimas 8 horas
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            order_id=f"ORD{random.randint(10000, 99999)}",
            notes=f"Movimiento de prueba {movement_type} para {product.product_name}"
        )
    
    # Generar movimientos históricos
    for day in range(num_days):
        current_date = start_date + timedelta(days=day)
        
        # Generar entre 2 y 4 movimientos por día
        num_movements = random.randint(2, 4)
        
        for i in range(num_movements):
            # Balancear entradas y salidas
            movement_type = random.choice(['INBOUND'] * 2 + ['OUTBOUND'] * 2)
            
            if movement_type == 'INBOUND':
                quantity = random.randint(inbound_min, inbound_max)
            else:
                quantity = random.randint(outbound_min, outbound_max)
                
                # Ocasionalmente generar un pico de ventas
                if random.random() < 0.05:  # 5% de probabilidad
                    quantity *= random.randint(2, 3)
            
            movement_id = f"M{movement_counter:04d}{product.product_id[-4:]}"
            movement_counter += 1
            
            try:
                InventoryMovement.objects.create(
                    movement_id=movement_id,
                    date=current_date + timedelta(hours=random.randint(9, 18)),  # Durante horas laborales
                    product=product,
                    movement_type=movement_type,
                    quantity=quantity,
                    order_id=f"ORD{random.randint(10000, 99999)}",
                    notes=f"Movimiento de prueba {movement_type} para {product.product_name}"
                )
            except Exception as e:
                print(f"Error al crear movimiento {movement_id}: {str(e)}")
                continue

def generate_data_for_all_products():
    # Obtener todos los productos
    products = Product.objects.all()
    
    for product in products:
        print(f"Generando datos para: {product.product_name}")
        generate_movement_data(product)
        print(f"✓ Datos generados para {product.product_name}")

if __name__ == "__main__":
    print("Iniciando generación de datos de prueba...")
    # Eliminar movimientos existentes para evitar duplicados
    InventoryMovement.objects.all().delete()
    print("Movimientos anteriores eliminados.")
    
    generate_data_for_all_products()
    print("\nGeneración de datos completada.")
    
    # Mostrar estadísticas
    total_movements = InventoryMovement.objects.count()
    print(f"\nEstadísticas:")
    print(f"Total de movimientos generados: {total_movements}")
    for product in Product.objects.all():
        product_movements = InventoryMovement.objects.filter(product=product).count()
        print(f"- {product.product_name}: {product_movements} movimientos") 