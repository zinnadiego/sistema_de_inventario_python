import os
import django
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from asgiref.sync import sync_to_async
from .predictor import AdvancedStockPredictor

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import Product, InventoryMovement, CurrentStock, PredictorStock
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

app = FastAPI(
    title="Inventory System API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# Modelos Pydantic para la API
class ProductBase(BaseModel):
    product_name: str
    sku: str
    unit_of_measure: str
    cost: float
    sale_price: float
    category: str
    location: str
    active: bool = True

class ProductCreate(ProductBase):
    product_id: str

class ProductResponse(ProductBase):
    product_id: str

    class Config:
        from_attributes = True

# Nuevo modelo Pydantic para predicciones
class StockPrediction(BaseModel):
    date: str
    predicted_quantity: float
    confidence_score: float
    model_used: str
    trend: str

# Crear instancia del predictor
stock_predictor = AdvancedStockPredictor()

async def authenticate_user(username: str, password: str):
    try:
        # Convertir la autenticación síncrona a asíncrona
        user = await sync_to_async(authenticate)(username=username, password=password)
        if user is not None and user.is_active:
            return user
    except Exception as e:
        print(f"Error en autenticación: {e}")
    return None

# Endpoints de autenticación
@app.post("/api/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}

# Endpoints de productos
@app.get("/api/products/", response_model=List[ProductResponse])
async def get_products(token: str = Depends(oauth2_scheme)):
    products = await sync_to_async(list)(Product.objects.all())
    return products

@app.post("/api/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, token: str = Depends(oauth2_scheme)):
    try:
        db_product = Product(**product.model_dump())
        await sync_to_async(db_product.save)()
        return db_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, token: str = Depends(oauth2_scheme)):
    try:
        product = await sync_to_async(Product.objects.get)(product_id=product_id)
        return product
    except Product.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

# Nuevo endpoint para predicciones
@app.get("/api/products/{product_id}/predict", response_model=List[StockPrediction])
async def predict_stock(product_id: str, days: int = 7, token: str = Depends(oauth2_scheme)):
    try:
        # Obtener historial de movimientos
        movements = await sync_to_async(list)(InventoryMovement.objects.filter(
            product__product_id=product_id
        ).order_by('date'))
        
        # Preparar datos históricos
        historical_data = [
            {
                'date': movement.date,
                'quantity': movement.quantity
            }
            for movement in movements
        ]
        
        # Si no hay suficientes datos, retornar error
        if len(historical_data) < 2:
            raise HTTPException(
                status_code=400,
                detail="No hay suficientes datos históricos para hacer una predicción"
            )
        
        # Realizar predicción
        predictions = stock_predictor.predict_next_days(historical_data, days)
        
        return predictions
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Punto de entrada para uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 