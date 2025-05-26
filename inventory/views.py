from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Product, InventoryMovement, CurrentStock
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

@csrf_exempt
def home(request):
    try:
        # Get dashboard statistics
        total_products = Product.objects.filter(active=True).count()
        total_stock = sum(stock.quantity for stock in CurrentStock.objects.all())
        
        # Get today's movements
        today = timezone.now().date()
        movements_today = InventoryMovement.objects.filter(
            date__date=today
        ).count()
        
        # Get products with low stock (less than 5 units)
        low_stock = CurrentStock.objects.filter(quantity__lt=5).count()
        
        # Get recent movements (last 10)
        recent_movements = InventoryMovement.objects.all().order_by('-date')[:10]
        
        # Get low stock items details
        low_stock_items = CurrentStock.objects.filter(
            quantity__lt=5
        ).select_related('product').order_by('quantity')[:5]
        
        context = {
            'total_products': total_products,
            'total_stock': total_stock,
            'movements_today': movements_today,
            'low_stock': low_stock,
            'recent_movements': recent_movements,
            'low_stock_items': low_stock_items,
        }
        
        return render(request, 'home.html', context)
    except Exception as e:
        print(f"Error en la vista home: {e}")
        context = {
            'error': str(e)
        }
        return render(request, 'home.html', context)
