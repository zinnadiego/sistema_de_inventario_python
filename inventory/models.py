from django.db import models

# Create your models here.

class Product(models.Model):
    product_id = models.CharField(max_length=10, primary_key=True)
    product_name = models.CharField(max_length=100)
    sku = models.CharField(max_length=20)
    unit_of_measure = models.CharField(max_length=20)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    location = models.CharField(max_length=10)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"

class InventoryMovement(models.Model):
    MOVEMENT_TYPES = [
        ('INBOUND', 'Inbound'),
        ('OUTBOUND', 'Outbound'),
        ('ADJUSTMENT_OUT', 'Adjustment Out'),
    ]

    movement_id = models.CharField(max_length=10, primary_key=True)
    date = models.DateTimeField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    order_id = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.movement_id} - {self.product.product_name}"

class CurrentStock(models.Model):
    STOCK_STATUS_CHOICES = [
        ('OK', 'OK'),
        ('CRITICAL', 'Critical'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    ]
    
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True)
    quantity = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)
    total_inventory_cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock_status = models.CharField(max_length=20, choices=STOCK_STATUS_CHOICES, default='OK')
    threshold = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.product.product_name} - Qty: {self.quantity}"

    def save(self, *args, **kwargs):
        # Actualizar el estado del stock basado en la cantidad y el umbral
        if self.quantity <= 0:
            self.stock_status = 'OUT_OF_STOCK'
        elif self.quantity <= self.threshold:
            self.stock_status = 'CRITICAL'
        else:
            self.stock_status = 'OK'
        
        # Calcular el costo total del inventario
        self.total_inventory_cost = self.quantity * self.product.cost
        
        super().save(*args, **kwargs)

class PredictorStock(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    units_sold = models.IntegerField()
    avg_sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    promotion_active = models.BooleanField(default=False)
    special_event = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('date', 'product')

    def __str__(self):
        return f"{self.product.product_name} - {self.date}"
