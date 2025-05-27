from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, Q
from .models import Product, InventoryMovement, CurrentStock
from django.views.decorators.csrf import csrf_exempt
from api.predictor import AdvancedStockPredictor
import json

# Create your views here.

def get_stock_threshold(product):
    """Define umbrales de stock bajo basados en el precio y categoría del producto"""
    if product.sale_price <= 10:  # Productos pequeños/baratos
        return 50
    elif product.sale_price <= 100:  # Productos medianos
        return 15
    elif product.sale_price <= 500:  # Productos grandes
        return 5
    else:  # Productos premium
        return 3

@csrf_exempt
def home(request):
    try:
        # Get dashboard statistics
        total_products = Product.objects.filter(active=True).count()
        
        # Obtener todos los stocks actuales
        current_stocks = CurrentStock.objects.select_related('product').all()
        total_stock = sum(stock.quantity for stock in current_stocks)
        
        # Filtrar productos con stock crítico o agotado
        critical_stock = current_stocks.filter(
            Q(stock_status='CRITICAL') | Q(stock_status='OUT_OF_STOCK')
        )
        
        print("=== DEBUG INFO ===")
        print(f"Productos críticos encontrados: {critical_stock.count()}")
        for stock in critical_stock:
            print(f"- {stock.product.product_name}: {stock.quantity}/{stock.threshold} ({stock.stock_status})")
        
        # Get today's movements considerando zona horaria
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        movements_today = InventoryMovement.objects.filter(
            date__gte=today_start
        ).count()
        
        # Get recent movements (last 10)
        recent_movements = InventoryMovement.objects.select_related('product').all().order_by('-date')[:10]
        
        # Obtener predicciones para productos críticos
        predictor = AdvancedStockPredictor()
        predictions = []
        
        for stock in critical_stock:
            try:
                # Obtener historial de movimientos de los últimos 30 días
                thirty_days_ago = timezone.now() - timedelta(days=30)
                movements = InventoryMovement.objects.filter(
                    product=stock.product,
                    date__gte=thirty_days_ago
                ).order_by('date')
                
                historical_data = [
                    {
                        'date': movement.date,
                        'quantity': movement.quantity
                    }
                    for movement in movements
                ]
                
                if len(historical_data) >= 2:  # Necesitamos al menos 2 puntos para predecir
                    next_week_pred = predictor.predict_next_days(historical_data, 7)
                    predictions.append({
                        'product': stock.product,
                        'current_stock': stock.quantity,
                        'threshold': stock.threshold,
                        'predictions': next_week_pred
                    })
                    print(f"Predicción generada para {stock.product.product_name}:")
                    print(f"- Stock actual: {stock.quantity}")
                    print(f"- Predicción a 7 días: {next_week_pred[-1]['predicted_quantity']}")
                    print(f"- Tendencia: {next_week_pred[-1].get('trend', 'No disponible')}")
            except Exception as e:
                print(f"Error al predecir para {stock.product}: {e}")
        
        context = {
            'total_products': total_products,
            'total_stock': total_stock,
            'movements_today': movements_today,
            'critical_stock_count': critical_stock.count(),
            'recent_movements': recent_movements,
            'critical_stock': critical_stock,
            'predictions': predictions,
        }
        
        print("\nContext data:")
        print(f"- Total productos: {total_products}")
        print(f"- Stock total: {total_stock}")
        print(f"- Movimientos hoy: {movements_today}")
        print(f"- Productos críticos: {critical_stock.count()}")
        print(f"- Predicciones generadas: {len(predictions)}")
        print("=== END DEBUG INFO ===")
        
        return render(request, 'home.html', context)
    except Exception as e:
        print(f"Error en la vista home: {e}")
        context = {
            'error': str(e)
        }
        return render(request, 'home.html', context)
