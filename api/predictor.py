import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedStockPredictor:
    def __init__(self):
        # Modelos de predicción
        self.linear_model = LinearRegression()
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = None
        self.confidence_score = 0.0
        
    def prepare_data(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara los datos históricos para el modelo.
        
        Args:
            historical_data: Lista de diccionarios con {'date': datetime, 'quantity': float}
            
        Returns:
            Tuple con features (X) y target (y)
        """
        if not historical_data:
            raise ValueError("No hay datos históricos para procesar")
            
        # Convertir fechas a números (días desde el primer registro)
        dates = np.array([d['date'] for d in historical_data])
        quantities = np.array([d['quantity'] for d in historical_data])
        
        # Detectar y manejar valores atípicos
        quantities = self._handle_outliers(quantities)
        
        # Crear features
        base_date = min(dates)
        days_feature = np.array([(d - base_date).days for d in dates])
        
        # Añadir características adicionales
        day_of_week = np.array([d.weekday() for d in dates])
        day_of_month = np.array([d.day for d in dates])
        month = np.array([d.month for d in dates])
        
        # Combinar features
        X = np.column_stack([
            days_feature,
            day_of_week,
            day_of_month,
            month
        ])
        
        # Escalar features
        X = self.scaler.fit_transform(X)
        
        return X, quantities
        
    def _handle_outliers(self, quantities: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """
        Maneja valores atípicos usando el método Z-score
        """
        z_scores = np.abs((quantities - np.mean(quantities)) / np.std(quantities))
        quantities[z_scores > threshold] = np.median(quantities)
        return quantities
        
    def _detect_trend(self, quantities: np.ndarray) -> str:
        """
        Detecta la tendencia en los datos
        """
        if len(quantities) < 2:
            return "No hay suficientes datos para detectar tendencia"
            
        slope = np.polyfit(np.arange(len(quantities)), quantities, 1)[0]
        
        if slope > 0.1:
            return "Tendencia al alza"
        elif slope < -0.1:
            return "Tendencia a la baja"
        else:
            return "Tendencia estable"
            
    def train(self, historical_data: List[Dict]) -> None:
        """
        Entrena múltiples modelos y selecciona el mejor
        """
        X, y = self.prepare_data(historical_data)
        
        # Dividir datos en entrenamiento y validación
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Entrenar modelos
        models = {
            'linear': self.linear_model,
            'random_forest': self.rf_model
        }
        
        best_score = -float('inf')
        
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_val)
            score = r2_score(y_val, y_pred)
            
            if score > best_score:
                best_score = score
                self.best_model = model
                self.best_model_name = name
                
        self.confidence_score = max(0, min(1, best_score))
        logger.info(f"Mejor modelo: {self.best_model_name} (Confianza: {self.confidence_score:.2f})")
        
    def predict_next_days(self, historical_data: List[Dict], days: int = 7) -> List[Dict]:
        """
        Predice el stock para los próximos días usando el mejor modelo.
        
        Args:
            historical_data: Datos históricos de stock
            days: Número de días a predecir
            
        Returns:
            Lista de predicciones con fecha, cantidad predicha y métricas
        """
        if not historical_data:
            return []
            
        # Entrenar modelos
        self.train(historical_data)
        
        # Preparar fechas para predicción
        last_date = max(d['date'] for d in historical_data)
        future_dates = [last_date + timedelta(days=i+1) for i in range(days)]
        
        # Crear features para predicción
        base_date = min(d['date'] for d in historical_data)
        days_feature = np.array([(d - base_date).days for d in future_dates])
        day_of_week = np.array([d.weekday() for d in future_dates])
        day_of_month = np.array([d.day for d in future_dates])
        month = np.array([d.month for d in future_dates])
        
        X_pred = np.column_stack([
            days_feature,
            day_of_week,
            day_of_month,
            month
        ])
        
        # Escalar features
        X_pred = self.scaler.transform(X_pred)
        
        # Realizar predicción
        predictions = self.best_model.predict(X_pred)
        
        # Detectar tendencia
        trend = self._detect_trend(np.array([d['quantity'] for d in historical_data]))
        
        # Formatear resultados
        return [
            {
                'date': date.strftime('%Y-%m-%d'),
                'predicted_quantity': max(0, float(quantity)),  # Evitar predicciones negativas
                'confidence_score': float(self.confidence_score),
                'model_used': self.best_model_name,
                'trend': trend
            }
            for date, quantity in zip(future_dates, predictions)
        ] 