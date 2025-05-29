import os
import django
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, conint
from asgiref.sync import sync_to_async
from .predictor import AdvancedStockPredictor
from decimal import Decimal
import uuid

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from inventory.models import Product, InventoryMovement, CurrentStock, PredictorStock
from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group

app = FastAPI(
    title="Sistema de Inventario API",
    description="""
    API para el sistema de gestión de inventario.
    
    ### Funcionalidades principales:
    * Autenticación de usuarios
    * Gestión de productos
    * Control de inventario
    * Predicción de stock
    * Gestión de usuarios
    """,
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar OAuth2 con la ruta correcta
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

# Modelos Pydantic para Usuarios
class UserBase(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    group: str  # "Administrador" o "Lectura"

class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    group: Optional[str] = None

class UserResponse(UserBase):
    id: int
    group: str

    @classmethod
    async def from_orm(cls, user):
        # Obtener el grupo del usuario de manera asíncrona
        groups = await sync_to_async(list)(user.groups.all())
        group_name = groups[0].name if groups else ""
        
        # Crear un diccionario con los datos del usuario
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "group": group_name
        }
        return cls(**user_data)

    class Config:
        from_attributes = True

# Modelo para actualización de producto
class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    sku: Optional[str] = None
    unit_of_measure: Optional[str] = None
    cost: Optional[float] = None
    sale_price: Optional[float] = None
    category: Optional[str] = None
    location: Optional[str] = None
    active: Optional[bool] = None

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
@app.post("/api/token", response_model=dict, tags=["Autenticación"], summary="Iniciar sesión")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint para autenticación de usuarios y obtención de token.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    return {"access_token": user.username, "token_type": "bearer"}

# Endpoints de productos
@app.get("/api/products/", response_model=List[ProductResponse], tags=["Productos"], summary="Listar productos")
async def get_products(token: str = Depends(oauth2_scheme)):
    """
    Obtiene la lista de todos los productos en el inventario.
    """
    products = await sync_to_async(list)(Product.objects.all())
    return products

@app.post("/api/products/", response_model=ProductResponse, tags=["Productos"], summary="Crear producto")
async def create_product(product: ProductCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea un nuevo producto en el inventario.
    """
    try:
        db_product = Product(**product.model_dump())
        await sync_to_async(db_product.save)()
        return db_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/products/{product_id}", response_model=ProductResponse, tags=["Productos"], summary="Obtener producto")
async def get_product(product_id: str, token: str = Depends(oauth2_scheme)):
    """
    Obtiene los detalles de un producto específico.
    """
    try:
        product = await sync_to_async(Product.objects.get)(product_id=product_id)
        return product
    except Product.DoesNotExist:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

# Nuevo endpoint para predicciones
@app.get("/api/products/{product_id}/predict", response_model=List[StockPrediction], tags=["Predicción"], summary="Predecir stock")
async def predict_stock(product_id: str, days: int = 7, token: str = Depends(oauth2_scheme)):
    """
    Realiza una predicción del stock para los próximos días.
    """
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

# Endpoints de usuarios
@app.post("/api/users/", response_model=UserResponse, tags=["Usuarios"], summary="Crear usuario")
async def create_user(user: UserCreate, token: str = Depends(oauth2_scheme)):
    """
    Crea un nuevo usuario en el sistema.
    """
    try:
        # Verificar si el usuario actual es administrador
        current_user = await sync_to_async(User.objects.get)(username=token)
        is_admin = await sync_to_async(lambda: current_user.groups.filter(name="Administrador").exists())()
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden crear usuarios"
            )

        # Verificar si el usuario ya existe
        exists = await sync_to_async(User.objects.filter(username=user.username).exists)()
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        # Crear el usuario
        new_user = User(
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )
        new_user.set_password(user.password)
        await sync_to_async(new_user.save)()

        # Asignar grupo
        group = await sync_to_async(Group.objects.get)(name=user.group)
        await sync_to_async(new_user.groups.add)(group)
        
        # Configurar is_staff si es administrador
        if user.group == "Administrador":
            new_user.is_staff = True
            await sync_to_async(new_user.save)()

        # Refrescar el usuario para obtener los datos actualizados
        new_user = await sync_to_async(User.objects.get)(id=new_user.id)
        return await UserResponse.from_orm(new_user)

    except Group.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Grupo inválido. Debe ser 'Administrador' o 'Lectura'"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuarios"], summary="Eliminar usuario")
async def delete_user(user_id: int, token: str = Depends(oauth2_scheme)):
    """
    Elimina un usuario del sistema.
    """
    try:
        # Verificar si el usuario actual es administrador
        current_user = await sync_to_async(User.objects.get)(username=token)
        is_admin = await sync_to_async(lambda: current_user.groups.filter(name="Administrador").exists())()
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden eliminar usuarios"
            )

        # Obtener y eliminar el usuario
        user = await sync_to_async(User.objects.get)(id=user_id)
        
        # Evitar que un administrador se elimine a sí mismo
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes eliminarte a ti mismo"
            )
            
        await sync_to_async(user.delete)()
        return None  # Retorna None para un 204 NO_CONTENT
        
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

@app.put("/api/users/{user_id}", response_model=UserResponse, tags=["Usuarios"], summary="Actualizar usuario")
async def update_user(user_id: int, user_update: UserUpdate, token: str = Depends(oauth2_scheme)):
    """
    Actualiza la información de un usuario existente.
    """
    try:
        # Verificar si el usuario actual es administrador
        current_user = await sync_to_async(User.objects.get)(username=token)
        is_admin = await sync_to_async(lambda: current_user.groups.filter(name="Administrador").exists())()
        
        if not is_admin and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo puedes actualizar tu propio usuario o ser administrador"
            )

        # Obtener el usuario a actualizar
        user = await sync_to_async(User.objects.get)(id=user_id)

        # Actualizar campos si se proporcionaron
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.first_name is not None:
            user.first_name = user_update.first_name
        if user_update.last_name is not None:
            user.last_name = user_update.last_name
        if user_update.password is not None:
            user.set_password(user_update.password)
        if user_update.is_active is not None and is_admin:  # Solo admin puede cambiar is_active
            user.is_active = user_update.is_active
        
        # Actualizar grupo si se proporciona y el usuario actual es admin
        if user_update.group is not None and is_admin:
            try:
                new_group = await sync_to_async(Group.objects.get)(name=user_update.group)
                await sync_to_async(user.groups.clear)()
                await sync_to_async(user.groups.add)(new_group)
                user.is_staff = (user_update.group == "Administrador")
            except Group.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Grupo inválido"
                )

        await sync_to_async(user.save)()
        
        # Refrescar el usuario para obtener los datos actualizados
        user = await sync_to_async(User.objects.get)(id=user.id)
        return await UserResponse.from_orm(user)

    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

@app.put("/api/products/{product_id}", response_model=ProductResponse, tags=["Productos"], summary="Actualizar producto")
async def update_product(product_id: str, product_update: ProductUpdate, token: str = Depends(oauth2_scheme)):
    """
    Actualiza la información de un producto existente.
    """
    try:
        # Verificar si el usuario actual es administrador
        current_user = await sync_to_async(User.objects.get)(username=token)
        is_admin = await sync_to_async(lambda: current_user.groups.filter(name="Administrador").exists())()
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden actualizar productos"
            )

        # Obtener el producto
        product = await sync_to_async(Product.objects.get)(product_id=product_id)

        # Actualizar campos si se proporcionaron
        if product_update.product_name is not None:
            product.product_name = product_update.product_name
        if product_update.sku is not None:
            product.sku = product_update.sku
        if product_update.unit_of_measure is not None:
            product.unit_of_measure = product_update.unit_of_measure
        if product_update.cost is not None:
            product.cost = product_update.cost
        if product_update.sale_price is not None:
            product.sale_price = product_update.sale_price
        if product_update.category is not None:
            product.category = product_update.category
        if product_update.location is not None:
            product.location = product_update.location
        if product_update.active is not None:
            product.active = product_update.active

        await sync_to_async(product.save)()
        return product

    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

# Modelos para Movimientos de Inventario
class MovementCreate(BaseModel):
    product_id: str
    quantity: Decimal
    movement_type: Literal["entrada", "salida"]
    description: Optional[str] = None

class MovementResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    quantity: Decimal
    movement_type: str
    description: Optional[str] = None
    date: datetime
    current_stock: Decimal

    class Config:
        from_attributes = True

# Modelo para actualización de stock
class StockUpdate(BaseModel):
    quantity: conint(gt=0)  # Asegura que la cantidad sea un entero positivo
    description: Optional[str] = None

# Constantes para tipos de movimiento
MOVEMENT_TYPE_MAPPING = {
    "entrada": "INBOUND",
    "salida": "OUTBOUND",
    "INBOUND": "entrada",
    "OUTBOUND": "salida"
}

# Endpoints de inventario
@app.post("/api/inventory/movements/", response_model=MovementResponse, tags=["Inventario"], summary="Crear movimiento")
async def create_movement(movement: MovementCreate, token: str = Depends(oauth2_scheme)):
    """
    Registra un nuevo movimiento de inventario (entrada o salida).
    """
    try:
        # Verificar si el usuario actual es administrador
        current_user = await sync_to_async(User.objects.get)(username=token)
        is_admin = await sync_to_async(lambda: current_user.groups.filter(name="Administrador").exists())()
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo los administradores pueden registrar movimientos"
            )

        # Obtener el producto
        product = await sync_to_async(Product.objects.get)(product_id=movement.product_id)
        
        # Obtener o crear el registro de stock actual
        current_stock = await sync_to_async(CurrentStock.objects.get_or_create)(
            product=product,
            defaults={'quantity': 0}
        )
        current_stock = current_stock[0]  # get_or_create devuelve una tupla (objeto, created)

        # Calcular nuevo stock
        quantity = movement.quantity
        if movement.movement_type == "salida":
            quantity = -quantity
            # Verificar si hay suficiente stock
            if current_stock.quantity + quantity < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay suficiente stock disponible"
                )

        # Generar movement_id (máximo 10 caracteres)
        prefix = "I" if movement.movement_type == "entrada" else "O"  # I para entrada (In), O para salida (Out)
        unique_id = uuid.uuid4().hex[:8]  # Tomamos solo los primeros 8 caracteres del UUID
        movement_id = f"{prefix}{unique_id[:8]}"  # Aseguramos que el ID total tenga 9 caracteres (1 del prefijo + 8 del UUID)

        # Crear el movimiento
        new_movement = InventoryMovement(
            movement_id=movement_id,
            product=product,
            quantity=abs(quantity),  # Guardamos la cantidad en positivo
            movement_type='INBOUND' if movement.movement_type == "entrada" else 'OUTBOUND',
            notes=movement.description,  # Cambiado de description a notes
            date=datetime.now(),
            order_id=movement_id  # Usar el mismo ID como order_id
        )
        await sync_to_async(new_movement.save)()

        # Actualizar stock actual
        current_stock.quantity += quantity
        await sync_to_async(current_stock.save)()

        # Preparar respuesta
        response_data = {
            "id": new_movement.movement_id,
            "product_id": product.product_id,
            "product_name": product.product_name,
            "quantity": abs(quantity),
            "movement_type": movement.movement_type,
            "description": new_movement.notes,
            "date": new_movement.date,
            "current_stock": current_stock.quantity
        }
        
        return MovementResponse(**response_data)

    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/api/inventory/movements/", response_model=List[MovementResponse], tags=["Inventario"], summary="Listar movimientos")
async def get_movements(
    product_id: Optional[str] = None,
    movement_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Obtiene la lista de movimientos de inventario con filtros opcionales.
    """
    try:
        # Construir el filtro base
        filter_kwargs = {}
        if product_id:
            filter_kwargs["product__product_id"] = product_id
        if movement_type:
            print(f"Filtering by movement_type: {movement_type}")  # Debug log
            # Convertir el tipo de movimiento a formato de base de datos
            movement_type_upper = movement_type.upper()
            if movement_type_upper == "OUTBOUND" or movement_type.lower() == "salida":
                filter_kwargs["movement_type"] = "OUTBOUND"
            elif movement_type_upper == "INBOUND" or movement_type.lower() == "entrada":
                filter_kwargs["movement_type"] = "INBOUND"
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo de movimiento inválido. Use 'entrada'/'INBOUND' o 'salida'/'OUTBOUND'"
                )
        
        if start_date:
            filter_kwargs["date__gte"] = start_date
        if end_date:
            filter_kwargs["date__lte"] = end_date

        print(f"Applied filters: {filter_kwargs}")  # Debug log

        # Obtener movimientos
        movements = await sync_to_async(list)(
            InventoryMovement.objects.filter(**filter_kwargs)
            .select_related('product')
            .order_by('-date')
        )

        print(f"Found {len(movements)} movements")  # Debug log

        # Preparar respuesta
        response_data = []
        for movement in movements:
            current_stock = await sync_to_async(CurrentStock.objects.get)(product=movement.product)
            # Convertir el tipo de movimiento al formato de respuesta
            movement_type_resp = MOVEMENT_TYPE_MAPPING.get(movement.movement_type, movement.movement_type)
            response_data.append({
                "id": movement.movement_id,
                "product_id": movement.product.product_id,
                "product_name": movement.product.product_name,
                "quantity": abs(movement.quantity),
                "movement_type": movement_type_resp,
                "description": movement.notes,
                "date": movement.date,
                "current_stock": current_stock.quantity
            })
        
        return response_data

    except Exception as e:
        print(f"Error in get_movements: {str(e)}")  # Debug log
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/inventory/stock/{product_id}/add", response_model=MovementResponse, tags=["Inventario"], summary="Agregar stock")
async def add_stock(product_id: str, stock_update: StockUpdate, token: str = Depends(oauth2_scheme)):
    """
    Agrega stock a un producto específico.
    """
    movement = MovementCreate(
        product_id=product_id,
        quantity=stock_update.quantity,
        movement_type="entrada",
        description=stock_update.description or "Adición de stock"
    )
    return await create_movement(movement, token)

@app.post("/api/inventory/stock/{product_id}/remove", response_model=MovementResponse, tags=["Inventario"], summary="Remover stock")
async def remove_stock(product_id: str, stock_update: StockUpdate, token: str = Depends(oauth2_scheme)):
    """
    Remueve stock de un producto específico.
    """
    movement = MovementCreate(
        product_id=product_id,
        quantity=stock_update.quantity,
        movement_type="salida",
        description=stock_update.description or "Remoción de stock"
    )
    return await create_movement(movement, token)

@app.get("/api/inventory/stock/", response_model=List[dict], tags=["Inventario"], summary="Obtener stock actual")
async def get_current_stock(token: str = Depends(oauth2_scheme)):
    """
    Obtiene el stock actual de todos los productos.
    """
    try:
        # Obtener todos los registros de stock actual
        stocks = await sync_to_async(list)(
            CurrentStock.objects.select_related('product').all()
        )

        # Preparar respuesta
        response_data = []
        for stock in stocks:
            response_data.append({
                "product_id": stock.product.product_id,
                "product_name": stock.product.product_name,
                "quantity": stock.quantity,
                "unit_of_measure": stock.product.unit_of_measure,
                "last_updated": stock.last_updated
            })
        
        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Punto de entrada para uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 