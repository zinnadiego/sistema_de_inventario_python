import os
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import Product, InventoryMovement, CurrentStock, PredictorStock

# Limpiar datos existentes
Product.objects.all().delete()
InventoryMovement.objects.all().delete()
CurrentStock.objects.all().delete()
PredictorStock.objects.all().delete()

# Crear productos
products_data = [
    {
        'product_id': 'P001',
        'product_name': 'Dell XPS 13 Laptop',
        'sku': 'DELL-XPS13',
        'unit_of_measure': 'Unit',
        'cost': 1200,
        'sale_price': 1500,
        'category': 'Electronics',
        'location': 'A1-01',
        'active': True
    },
    {
        'product_id': 'P002',
        'product_name': 'LG UltraWide Monitor',
        'sku': 'LG-UW34',
        'unit_of_measure': 'Unit',
        'cost': 350,
        'sale_price': 450,
        'category': 'Electronics',
        'location': 'A1-02',
        'active': True
    },
    {
        'product_id': 'P003',
        'product_name': 'RGB Mechanical Keyboard',
        'sku': 'KM-RGB01',
        'unit_of_measure': 'Unit',
        'cost': 80,
        'sale_price': 120,
        'category': 'Peripherals',
        'location': 'B2-05',
        'active': True
    },
    {
        'product_id': 'P004',
        'product_name': 'Logitech Gaming Mouse',
        'sku': 'LOGI-G502',
        'unit_of_measure': 'Unit',
        'cost': 50,
        'sale_price': 75,
        'category': 'Peripherals',
        'location': 'B2-06',
        'active': True
    },
    {
        'product_id': 'P005',
        'product_name': 'HDMI Cable 2m',
        'sku': 'HDMI-2M',
        'unit_of_measure': 'Unit',
        'cost': 5,
        'sale_price': 10,
        'category': 'Accessories',
        'location': 'C3-10',
        'active': True
    }
]

# Insertar productos
for product_data in products_data:
    Product.objects.create(**product_data)

# Crear movimientos de inventario
movements_data = [
    {
        'movement_id': 'M001',
        'date': datetime(2024, 5, 20, 9, 0),
        'product_id': 'P001',
        'movement_type': 'INBOUND',
        'quantity': 10,
        'order_id': 'PO-1001',
        'notes': 'Supplier reception'
    },
    {
        'movement_id': 'M002',
        'date': datetime(2024, 5, 20, 10, 30),
        'product_id': 'P003',
        'movement_type': 'INBOUND',
        'quantity': 20,
        'order_id': 'PO-1002',
        'notes': 'Supplier reception'
    },
    {
        'movement_id': 'M003',
        'date': datetime(2024, 5, 20, 14, 15),
        'product_id': 'P001',
        'movement_type': 'OUTBOUND',
        'quantity': 1,
        'order_id': 'SO-2001',
        'notes': 'Sale to customer John Doe'
    },
    {
        'movement_id': 'M004',
        'date': datetime(2024, 5, 20, 16, 0),
        'product_id': 'P005',
        'movement_type': 'INBOUND',
        'quantity': 50,
        'order_id': 'PO-1003',
        'notes': 'New purchase'
    },
    {
        'movement_id': 'M005',
        'date': datetime(2024, 5, 21, 9, 0),
        'product_id': 'P002',
        'movement_type': 'INBOUND',
        'quantity': 5,
        'order_id': 'PO-1004',
        'notes': 'Urgent reception'
    },
    {
        'movement_id': 'M006',
        'date': datetime(2024, 5, 21, 11, 45),
        'product_id': 'P004',
        'movement_type': 'OUTBOUND',
        'quantity': 2,
        'order_id': 'SO-2002',
        'notes': 'Sale to customer Jane Doe'
    },
    {
        'movement_id': 'M007',
        'date': datetime(2024, 5, 21, 13, 0),
        'product_id': 'P001',
        'movement_type': 'OUTBOUND',
        'quantity': 1,
        'order_id': 'SO-2003',
        'notes': 'Customer return (exchange)'
    },
    {
        'movement_id': 'M008',
        'date': datetime(2024, 5, 21, 15, 30),
        'product_id': 'P003',
        'movement_type': 'ADJUSTMENT_OUT',
        'quantity': 1,
        'order_id': 'ADJ-001',
        'notes': 'Warehouse damage'
    }
]

# Insertar movimientos
for movement_data in movements_data:
    product = Product.objects.get(product_id=movement_data['product_id'])
    movement_data['product'] = product
    del movement_data['product_id']
    InventoryMovement.objects.create(**movement_data)

# Crear stock actual
current_stock_data = [
    {
        'product_id': 'P001',
        'quantity': 8,
        'last_updated': datetime(2024, 5, 21, 13, 0),
        'total_inventory_cost': 9600
    },
    {
        'product_id': 'P002',
        'quantity': 5,
        'last_updated': datetime(2024, 5, 21, 9, 0),
        'total_inventory_cost': 1750
    },
    {
        'product_id': 'P003',
        'quantity': 19,
        'last_updated': datetime(2024, 5, 21, 15, 30),
        'total_inventory_cost': 1520
    },
    {
        'product_id': 'P004',
        'quantity': 18,
        'last_updated': datetime(2024, 5, 21, 11, 45),
        'total_inventory_cost': 900
    },
    {
        'product_id': 'P005',
        'quantity': 50,
        'last_updated': datetime(2024, 5, 20, 16, 0),
        'total_inventory_cost': 250
    }
]

# Insertar stock actual
for stock_data in current_stock_data:
    product = Product.objects.get(product_id=stock_data['product_id'])
    del stock_data['product_id']
    CurrentStock.objects.create(product=product, **stock_data)

# Crear datos de predicción
predictor_data = [
    {
        'date': datetime(2024, 1, 1).date(),
        'product_id': 'P001',
        'units_sold': 5,
        'avg_sale_price': 1500,
        'promotion_active': False,
        'special_event': "New Year's Day"
    },
    {
        'date': datetime(2024, 1, 1).date(),
        'product_id': 'P002',
        'units_sold': 2,
        'avg_sale_price': 450,
        'promotion_active': False,
        'special_event': "New Year's Day"
    },
    {
        'date': datetime(2024, 1, 8).date(),
        'product_id': 'P001',
        'units_sold': 7,
        'avg_sale_price': 1500,
        'promotion_active': True,
        'special_event': None
    },
    {
        'date': datetime(2024, 1, 8).date(),
        'product_id': 'P003',
        'units_sold': 10,
        'avg_sale_price': 120,
        'promotion_active': False,
        'special_event': None
    },
    {
        'date': datetime(2024, 1, 15).date(),
        'product_id': 'P001',
        'units_sold': 4,
        'avg_sale_price': 1500,
        'promotion_active': False,
        'special_event': None
    },
    {
        'date': datetime(2024, 5, 15).date(),
        'product_id': 'P001',
        'units_sold': 6,
        'avg_sale_price': 1450,
        'promotion_active': True,
        'special_event': None
    },
    {
        'date': datetime(2024, 5, 15).date(),
        'product_id': 'P004',
        'units_sold': 3,
        'avg_sale_price': 75,
        'promotion_active': False,
        'special_event': None
    }
]

# Insertar datos de predicción
for predictor_item in predictor_data:
    product = Product.objects.get(product_id=predictor_item['product_id'])
    del predictor_item['product_id']
    PredictorStock.objects.create(product=product, **predictor_item)

print("Datos cargados exitosamente!") 