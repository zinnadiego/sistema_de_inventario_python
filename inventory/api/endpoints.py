from fastapi import APIRouter, Depends, HTTPException, status
from django.contrib.auth.models import User, Group
from django.db import transaction
from typing import List
from .schemas import (
    UserCreate, UserUpdate, UserResponse, ProductUpdate,
    StockMovement, StockUpdate, ProductMovementResponse
)
from ..models import Product, InventoryMovement, CurrentStock
from datetime import datetime
import uuid

router = APIRouter()

# Endpoints de Usuarios
@router.get("/users/", response_model=List[UserResponse])
async def get_users():
    users = User.objects.all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            groups=[g.name for g in user.groups.all()]
        ) for user in users
    ]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    try:
        user = User.objects.get(id=user_id)
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            groups=[g.name for g in user.groups.all()]
        )
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

@router.post("/users/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    try:
        with transaction.atomic():
            # Verificar si el grupo existe
            try:
                group = Group.objects.get(name=user_data.group)
            except Group.DoesNotExist:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El grupo {user_data.group} no existe"
                )

            # Crear el usuario
            user = User.objects.create_user(
                username=user_data.username,
                email=user_data.email,
                password=user_data.password,
                first_name=user_data.first_name or "",
                last_name=user_data.last_name or "",
                is_active=user_data.is_active
            )

            # Asignar grupo y permisos
            user.groups.add(group)
            user.is_staff = (group.name == 'Administrador')
            user.save()

            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                groups=[g.name for g in user.groups.all()]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate):
    try:
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            
            if user_data.email is not None:
                user.email = user_data.email
            if user_data.first_name is not None:
                user.first_name = user_data.first_name
            if user_data.last_name is not None:
                user.last_name = user_data.last_name
            if user_data.is_active is not None:
                user.is_active = user_data.is_active
            if user_data.password is not None:
                user.set_password(user_data.password)
            if user_data.group is not None:
                try:
                    group = Group.objects.get(name=user_data.group)
                    user.groups.clear()
                    user.groups.add(group)
                    user.is_staff = (group.name == 'Administrador')
                except Group.DoesNotExist:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"El grupo {user_data.group} no existe"
                    )
            
            user.save()
            
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_active=user.is_active,
                groups=[g.name for g in user.groups.all()]
            )
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return {"message": "Usuario eliminado correctamente"}
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

# Endpoints de Productos
@router.put("/products/{product_id}", response_model=dict)
async def update_product(product_id: str, product_data: ProductUpdate):
    try:
        product = Product.objects.get(product_id=product_id)
        
        if product_data.product_name is not None:
            product.product_name = product_data.product_name
        if product_data.sku is not None:
            product.sku = product_data.sku
        if product_data.category is not None:
            product.category = product_data.category
        if product_data.cost is not None:
            product.cost = product_data.cost
        if product_data.sale_price is not None:
            product.sale_price = product_data.sale_price
        if product_data.active is not None:
            product.active = product_data.active
            
        product.save()
        return {"message": "Producto actualizado correctamente"}
    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    try:
        product = Product.objects.get(product_id=product_id)
        product.delete()
        return {"message": "Producto eliminado correctamente"}
    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

# Endpoints de Movimientos de Stock
@router.post("/products/{product_id}/sell", response_model=ProductMovementResponse)
async def sell_product(product_id: str, movement: StockMovement):
    try:
        with transaction.atomic():
            product = Product.objects.get(product_id=product_id)
            current_stock = CurrentStock.objects.get(product=product)
            
            if current_stock.quantity < movement.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Stock insuficiente"
                )
            
            # Crear movimiento de salida
            movement_id = f"OUT-{uuid.uuid4().hex[:8].upper()}"
            inventory_movement = InventoryMovement.objects.create(
                movement_id=movement_id,
                date=datetime.now(),
                product=product,
                movement_type='OUTBOUND',
                quantity=movement.quantity,
                order_id=movement.order_id
            )
            
            # Actualizar stock
            current_stock.quantity -= movement.quantity
            current_stock.save()
            
            return ProductMovementResponse(
                movement_id=inventory_movement.movement_id,
                date=inventory_movement.date,
                product_id=product.product_id,
                movement_type=inventory_movement.movement_type,
                quantity=inventory_movement.quantity,
                order_id=inventory_movement.order_id,
                current_stock=current_stock.quantity
            )
    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    except CurrentStock.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stock no encontrado"
        )

@router.post("/products/{product_id}/buy", response_model=ProductMovementResponse)
async def buy_product(product_id: str, movement: StockMovement):
    try:
        with transaction.atomic():
            product = Product.objects.get(product_id=product_id)
            current_stock, created = CurrentStock.objects.get_or_create(
                product=product,
                defaults={'quantity': 0}
            )
            
            # Crear movimiento de entrada
            movement_id = f"IN-{uuid.uuid4().hex[:8].upper()}"
            inventory_movement = InventoryMovement.objects.create(
                movement_id=movement_id,
                date=datetime.now(),
                product=product,
                movement_type='INBOUND',
                quantity=movement.quantity,
                order_id=movement.order_id
            )
            
            # Actualizar stock
            current_stock.quantity += movement.quantity
            current_stock.save()
            
            return ProductMovementResponse(
                movement_id=inventory_movement.movement_id,
                date=inventory_movement.date,
                product_id=product.product_id,
                movement_type=inventory_movement.movement_type,
                quantity=inventory_movement.quantity,
                order_id=inventory_movement.order_id,
                current_stock=current_stock.quantity
            )
    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

@router.put("/products/{product_id}/stock", response_model=dict)
async def update_stock(product_id: str, stock_data: StockUpdate):
    try:
        with transaction.atomic():
            product = Product.objects.get(product_id=product_id)
            current_stock, created = CurrentStock.objects.get_or_create(
                product=product,
                defaults={'quantity': 0}
            )
            
            # Calcular la diferencia para crear el movimiento
            difference = stock_data.quantity - current_stock.quantity
            
            if difference < 0:
                # Crear movimiento de ajuste de salida
                movement_id = f"ADJ-{uuid.uuid4().hex[:8].upper()}"
                InventoryMovement.objects.create(
                    movement_id=movement_id,
                    date=datetime.now(),
                    product=product,
                    movement_type='ADJUSTMENT_OUT',
                    quantity=abs(difference),
                    order_id=f"ADJ-{movement_id}"
                )
            
            # Actualizar stock
            current_stock.quantity = stock_data.quantity
            current_stock.save()
            
            return {
                "message": "Stock actualizado correctamente",
                "current_stock": current_stock.quantity
            }
    except Product.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

# Endpoint para listar movimientos de inventario
@router.get("/inventory/movements/")
async def get_movements(product_id: str = None, movement_type: str = None):
    try:
        # Construir el query base
        query = InventoryMovement.objects.all()
        
        # Aplicar filtros si se proporcionan
        if product_id:
            query = query.filter(product__product_id=product_id)
        if movement_type:
            # Mapear los tipos de movimiento amigables a los valores del modelo
            movement_type_map = {
                'salida': 'OUTBOUND',
                'entrada': 'INBOUND',
                'ajuste': 'ADJUSTMENT_OUT'
            }
            model_movement_type = movement_type_map.get(movement_type.lower())
            if model_movement_type:
                query = query.filter(movement_type=model_movement_type)
            
        # Obtener los movimientos
        movements = list(query.select_related('product'))
        
        # Convertir a formato de respuesta manualmente
        response_data = []
        for mov in movements:
            current_stock = CurrentStock.objects.get(product=mov.product).quantity
            movement_data = {
                "movement_id": str(mov.movement_id),
                "date": mov.date.isoformat(),
                "product_id": str(mov.product.product_id),
                "movement_type": str(mov.movement_type),
                "quantity": int(mov.quantity),
                "order_id": str(mov.order_id) if mov.order_id else None,
                "current_stock": int(current_stock)
            }
            response_data.append(movement_data)
            
        return response_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 