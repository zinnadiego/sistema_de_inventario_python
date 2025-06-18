from django.test import TestCase
from django.utils import timezone
from .models import Product, CurrentStock

# Create your tests here.

class ProductModelTest(TestCase):
    def setUp(self):
        # Crear un producto de prueba
        self.product = Product.objects.create(
            product_id="TEST001",
            product_name="Test Product",
            sku="SKU001",
            unit_of_measure="UN",
            cost=10.00,
            sale_price=15.00,
            category="Test",
            location="A1",
            active=True
        )

    def test_product_creation(self):
        """Test que verifica la creación correcta de un producto"""
        self.assertEqual(self.product.product_name, "Test Product")
        self.assertEqual(self.product.sku, "SKU001")
        self.assertTrue(self.product.active)

    def test_product_string_representation(self):
        """Test que verifica la representación en string del producto"""
        expected_string = "Test Product (TEST001)"
        self.assertEqual(str(self.product), expected_string)

class CurrentStockModelTest(TestCase):
    def setUp(self):
        # Crear un producto y su stock actual
        self.product = Product.objects.create(
            product_id="TEST002",
            product_name="Test Product 2",
            sku="SKU002",
            unit_of_measure="UN",
            cost=20.00,
            sale_price=30.00,
            category="Test",
            location="A2",
            active=True
        )
        self.stock = CurrentStock.objects.create(
            product=self.product,
            quantity=10,
            threshold=5
        )

    def test_stock_creation(self):
        """Test que verifica la creación correcta del stock"""
        self.assertEqual(self.stock.quantity, 10)
        self.assertEqual(self.stock.threshold, 5)
        self.assertEqual(self.stock.stock_status, "OK")

    def test_stock_status_update(self):
        """Test que verifica la actualización del estado del stock"""
        # Probar estado crítico
        self.stock.quantity = 5
        self.stock.save()
        self.assertEqual(self.stock.stock_status, "CRITICAL")

        # Probar estado fuera de stock
        self.stock.quantity = 0
        self.stock.save()
        self.assertEqual(self.stock.stock_status, "OUT_OF_STOCK")

    def test_total_inventory_cost(self):
        """Test que verifica el cálculo del costo total del inventario"""
        self.assertEqual(self.stock.total_inventory_cost, 200.00)  # 10 unidades * $20.00
