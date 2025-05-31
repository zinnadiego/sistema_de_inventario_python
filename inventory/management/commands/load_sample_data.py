from django.core.management.base import BaseCommand
from inventory.models import Product, InventoryMovement, CurrentStock, PredictorStock
from django.utils import timezone
import random
from datetime import timedelta
import uuid
import string
from decimal import Decimal

class Command(BaseCommand):
    help = 'Carga datos de ejemplo en la base de datos'

    def generate_short_id(self):
        """Genera un ID único de 4 caracteres"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choices(chars, k=4))

    def handle(self, *args, **kwargs):
        # Crear productos
        products = [
            {
                'product_id': 'LAP001',
                'product_name': 'Laptop ThinkPad X1',
                'sku': 'LAP-001',
                'unit_of_measure': 'unidad',
                'cost': 999.99,
                'sale_price': 1299.99,
                'category': 'Laptops',
                'location': 'A1'
            },
            {
                'product_id': 'MON001',
                'product_name': 'Monitor Dell 27"',
                'sku': 'MON-001',
                'unit_of_measure': 'unidad',
                'cost': 299.99,
                'sale_price': 399.99,
                'category': 'Monitores',
                'location': 'A2'
            },
            {
                'product_id': 'KEY001',
                'product_name': 'Teclado Mecánico',
                'sku': 'KEY-001',
                'unit_of_measure': 'unidad',
                'cost': 89.99,
                'sale_price': 129.99,
                'category': 'Periféricos',
                'location': 'B1'
            },
            {
                'product_id': 'MOU001',
                'product_name': 'Mouse Inalámbrico',
                'sku': 'MOU-001',
                'unit_of_measure': 'unidad',
                'cost': 29.99,
                'sale_price': 49.99,
                'category': 'Periféricos',
                'location': 'B2'
            },
            {
                'product_id': 'SSD001',
                'product_name': 'Disco SSD 1TB',
                'sku': 'SSD-001',
                'unit_of_measure': 'unidad',
                'cost': 119.99,
                'sale_price': 159.99,
                'category': 'Almacenamiento',
                'location': 'C1'
            }
        ]

        # Crear los productos
        created_products = []
        for product_data in products:
            product, created = Product.objects.get_or_create(
                product_id=product_data['product_id'],
                defaults=product_data
            )
            created_products.append(product)
            if created:
                self.stdout.write(f'Producto creado: {product.product_name}')
                # Crear stock inicial
                CurrentStock.objects.create(
                    product=product,
                    quantity=random.randint(30, 50),
                    total_inventory_cost=product.cost * 30,
                    stock_status='OK',
                    threshold=10
                )
            else:
                self.stdout.write(f'Producto ya existente: {product.product_name}')

        # Crear movimientos de inventario
        movement_types = ['INBOUND', 'OUTBOUND']
        dates = [
            timezone.now() - timedelta(days=x) 
            for x in range(30)  # Últimos 30 días
        ]

        # Diccionario para rastrear ventas diarias por producto
        daily_sales = {}
        used_movement_ids = set()  # Para asegurar IDs únicos

        for product in created_products:
            daily_sales[product.product_id] = {}
            
            for date in dates:
                daily_sales[product.product_id][date.date()] = 0
                
                if random.random() < 0.7:  # 70% de probabilidad de crear un movimiento
                    movement_type = random.choice(movement_types)
                    quantity = random.randint(1, 10)
                    
                    if movement_type == 'OUTBOUND':
                        current_stock = CurrentStock.objects.get(product=product)
                        quantity = min(quantity, current_stock.quantity)
                        if quantity <= 0:
                            continue
                        # Registrar venta para predicciones
                        daily_sales[product.product_id][date.date()] = quantity
                    
                    # Generar un ID único corto
                    while True:
                        movement_id = f"{product.product_id[:2]}{self.generate_short_id()}"[:10]
                        if movement_id not in used_movement_ids:
                            used_movement_ids.add(movement_id)
                            break
                    
                    InventoryMovement.objects.create(
                        movement_id=movement_id,
                        product=product,
                        quantity=quantity,
                        movement_type=movement_type,
                        date=date,
                        order_id=f"ORD-{date.strftime('%Y%m%d')}-{random.randint(1,999):03d}",
                        notes=f'{movement_type} de inventario'
                    )
                    
                    # Actualizar el stock actual
                    current_stock = CurrentStock.objects.get(product=product)
                    if movement_type == 'INBOUND':
                        current_stock.quantity += quantity
                    else:
                        current_stock.quantity -= quantity
                    current_stock.total_inventory_cost = current_stock.quantity * product.cost
                    current_stock.save()
                    
                    self.stdout.write(f'Movimiento creado para {product.product_name}: {movement_type} de {quantity} unidades')

        # Crear datos de predicción
        self.stdout.write("Creando datos de predicción...")
        special_events = ['Cyber Monday', 'Black Friday', 'Navidad', 'Año Nuevo']
        
        for product in created_products:
            for date, units_sold in daily_sales[product.product_id].items():
                # Aplicar algunas variaciones en el precio de venta (usando Decimal)
                price_variation = Decimal(str(random.uniform(0.9, 1.1)))
                avg_sale_price = product.sale_price * price_variation
                
                # Determinar si hay evento especial (10% de probabilidad)
                special_event = random.choice(special_events) if random.random() < 0.1 else None
                
                # Determinar si hay promoción (20% de probabilidad)
                promotion_active = random.random() < 0.2
                
                PredictorStock.objects.create(
                    date=date,
                    product=product,
                    units_sold=units_sold,
                    avg_sale_price=avg_sale_price.quantize(Decimal('0.01')),  # Redondear a 2 decimales
                    promotion_active=promotion_active,
                    special_event=special_event
                )
                self.stdout.write(f'Datos de predicción creados para {product.product_name} en {date}')

        self.stdout.write(self.style.SUCCESS('Datos de ejemplo cargados exitosamente')) 