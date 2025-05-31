from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, Q
from .models import Product, InventoryMovement, CurrentStock
from django.views.decorators.csrf import csrf_exempt
from api.predictor import AdvancedStockPredictor
from django.core.serializers.json import DjangoJSONEncoder
import json
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

def serialize_prediction_data(prediction):
    """Serializa los datos de predicción para uso en JavaScript"""
    try:
        serialized = {
            'product': {
                'id': prediction['product'].product_id,
                'product_name': prediction['product'].product_name
            },
            'current_stock': prediction['current_stock'],
            'threshold': prediction['threshold'],
            'predictions': []
        }
        
        # Asegurarse de que las predicciones sean serializables
        for pred in prediction['predictions']:
            serialized['predictions'].append({
                'date': pred['date'],
                'predicted_quantity': float(pred['predicted_quantity']),
                'confidence_score': float(pred['confidence_score']),
                'model_used': str(pred['model_used']),
                'trend': str(pred['trend'])
            })
            
        logger.info(f"Predicción serializada para {prediction['product'].product_name}: {json.dumps(serialized, cls=DjangoJSONEncoder)}")
        return serialized
    except Exception as e:
        logger.error(f"Error serializando predicción: {str(e)}")
        return None

@csrf_exempt
def home(request):
    try:
        logger.info("Iniciando vista home")
        
        # Get dashboard statistics
        total_products = Product.objects.filter(active=True).count()
        logger.info(f"Total productos activos: {total_products}")
        
        # Obtener todos los stocks actuales
        current_stocks = CurrentStock.objects.select_related('product').all()
        total_stock = sum(stock.quantity for stock in current_stocks)
        logger.info(f"Stock total: {total_stock}")
        
        # Filtrar productos con stock crítico o agotado
        critical_stock = []
        critical_stock_count = 0
        
        for stock in current_stocks:
            if stock.quantity <= 0:
                stock.stock_status = 'OUT_OF_STOCK'
                critical_stock.append(stock)
                critical_stock_count += 1
            elif stock.quantity <= stock.threshold:
                stock.stock_status = 'CRITICAL'
                critical_stock.append(stock)
                critical_stock_count += 1
            else:
                stock.stock_status = 'OK'
            stock.save()
        
        logger.info(f"Productos en stock crítico: {critical_stock_count}")
        
        # Get today's movements
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        movements_today = InventoryMovement.objects.filter(
            date__gte=today_start
        ).count()
        logger.info(f"Movimientos hoy: {movements_today}")
        
        # Get recent movements (last 10)
        recent_movements = InventoryMovement.objects.select_related('product').all().order_by('-date')[:10]
        
        # Obtener predicciones para todos los productos
        predictor = AdvancedStockPredictor()
        serialized_predictions = []
        
        logger.info("Generando predicciones para productos")
        for stock in current_stocks:
            try:
                logger.info(f"Procesando predicción para {stock.product.product_name}")
                # Obtener historial de movimientos de los últimos 30 días
                thirty_days_ago = timezone.now() - timedelta(days=30)
                movements = InventoryMovement.objects.filter(
                    product=stock.product,
                    date__gte=thirty_days_ago
                ).order_by('date')
                
                logger.info(f"Movimientos encontrados: {movements.count()}")
                
                historical_data = [
                    {
                        'date': movement.date,
                        'quantity': movement.quantity
                    }
                    for movement in movements
                ]
                
                if len(historical_data) >= 2:
                    logger.info("Generando predicción...")
                    next_week_pred = predictor.predict_next_days(historical_data, 7)
                    prediction_data = {
                        'product': stock.product,
                        'current_stock': stock.quantity,
                        'threshold': stock.threshold,
                        'predictions': next_week_pred
                    }
                    serialized_prediction = serialize_prediction_data(prediction_data)
                    if serialized_prediction:
                        serialized_predictions.append(serialized_prediction)
                        logger.info(f"Predicción generada exitosamente para {stock.product.product_name}")
                else:
                    logger.warning(f"No hay suficientes datos históricos para {stock.product.product_name}")
            except Exception as e:
                logger.error(f"Error al predecir para {stock.product.product_name}: {str(e)}")
        
        # Convertir predicciones a JSON
        try:
            predictions_json = json.dumps(serialized_predictions, cls=DjangoJSONEncoder)
            logger.info(f"Total de predicciones generadas: {len(serialized_predictions)}")
        except Exception as e:
            logger.error(f"Error al serializar predicciones a JSON: {str(e)}")
            predictions_json = "[]"
        
        context = {
            'total_products': total_products,
            'total_stock': total_stock,
            'movements_today': movements_today,
            'critical_stock_count': critical_stock_count,
            'recent_movements': recent_movements,
            'critical_stock': critical_stock,
            'predictions': predictions_json,
        }
        
        logger.info("Vista home completada exitosamente")
        return render(request, 'home.html', context)
    except Exception as e:
        logger.error(f"Error en la vista home: {str(e)}")
        context = {
            'error': str(e)
        }
        return render(request, 'home.html', context)
