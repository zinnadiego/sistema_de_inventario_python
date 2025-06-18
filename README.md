# Sistema de Inventario

Este proyecto es un sistema de gestión de inventario que combina Django y FastAPI para proporcionar una robusta aplicación web con una API RESTful y capacidades predictivas de stock.

## Características Principales

- **Dashboard en Tiempo Real**: Visualización de estadísticas clave y estado del inventario
- **Predicciones Inteligentes**: Sistema predictivo que analiza tendencias de stock
- **Alertas Automáticas**: Notificaciones de stock crítico y tendencias negativas
- **API REST Completa**: Endpoints para todas las operaciones de inventario
- **Interfaz Moderna**: UI/UX optimizada con gráficos interactivos
- **Sistema de Roles**: Control de acceso basado en roles

## Formas de Instalación

Hay dos formas de ejecutar el sistema:
1. Usando Docker (recomendado para producción)
2. Instalación local (recomendado para desarrollo)

### 1. Instalación con Docker

1. **Clonar el repositorio**:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. **Iniciar con Docker Compose**:
```bash
docker-compose up -d
```

3. **Crear superusuario** (primera vez):
```bash
docker-compose exec web python create_superuser.py
```

4. **Cargar datos de ejemplo**:
```bash
docker-compose exec web python manage.py load_sample_data
```

5. **Acceder al sistema**:
- Frontend y API: http://localhost:8001
- Panel de administración: http://localhost:8001/admin
- Documentación API: http://localhost:8001/docs

### Manejar contenedores

1. **Detener los contenedores** (no borra los datos):
```bash
docker-compose down
```

2. **Reiniciar los contenedores** (los datos se mantienen):
```bash
docker-compose up -d
```

3. **Si quieres borrar TODO** (¡esto SÍ borrará los datos!):
```bash
docker-compose down -v
```

4. **Hacer backup de los datos** (opcional, pero recomendado):
```bash
# Obtener el ID del contenedor de PostgreSQL
docker ps

# Hacer backup de la base de datos
docker exec -t [ID_CONTENEDOR_POSTGRES] pg_dump -U postgres inventory_db > backup_inventory.sql
```

IMPORTANTE: 
- Los datos persisten mientras no elimines los volúmenes de Docker
- Usar `docker-compose down` es seguro, mantiene los datos
- Solo se pierden los datos si usas `docker-compose down -v` o borras manualmente los volúmenes

### 2. Instalación Local (Sin Docker)

1. **Crear y activar el entorno virtual**:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar PostgreSQL**:
- Instalar PostgreSQL si no está instalado
- Crear una base de datos nueva:
```sql
CREATE DATABASE inventory_db;
```
- Copiar `.env.example` a `.env` y configurar:
```
DEBUG=True
# Puedes usar esta SECRET_KEY para desarrollo local
SECRET_KEY=django-insecure-m9ouo=^vl*yy^nqedux704q4ei7vt0d*lnt(vj7j#3u$-0g%xb
DB_NAME=inventory_db
DB_USER=tu_usuario_db
DB_PASSWORD=tu_contraseña_db
DB_HOST=localhost
DB_PORT=5432
```

NOTA: En un ambiente de producción, deberías generar una nueva SECRET_KEY. Puedes generarla usando:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. **Aplicar migraciones**:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crear superusuario y grupos**:
```bash
python create_superuser.py
# Esto crea:
# - Usuario: admin, Contraseña: Admin123!
# - Grupos: Administrador y Lectura
```

6. **Cargar datos de ejemplo**:
```bash
python manage.py load_sample_data
# Carga productos como Dell XPS 13, LG Monitor, etc.
```

7. **Recolectar archivos estáticos**:
```bash
python manage.py collectstatic --noinput
```

8. **Iniciar el servidor**:
```bash
python manage.py runserver 8001
```

9. **Acceder al sistema**:
- Frontend y API: http://localhost:8001
- Panel de administración: http://localhost:8001/admin
- Documentación API: http://localhost:8001/docs

## Ejecución de Tests

El proyecto incluye una suite de tests automatizados. Hay varias formas de ejecutarlos:

### 1. Ejecutar todos los tests
```bash
# Usando Docker (recomendado)
docker-compose exec web python manage.py test

# Localmente (sin Docker)
python manage.py test
```

### 2. Ver resultados detallados
```bash
# Modo verbose (muestra más detalles)
docker-compose exec web python manage.py test -v 2

# Modo muy detallado (muestra todo)
docker-compose exec web python manage.py test -v 3
```

### 3. Ejecutar tests específicos
```bash
# Ejecutar tests de una app específica
docker-compose exec web python manage.py test inventory

# Ejecutar un test específico
docker-compose exec web python manage.py test inventory.tests.ProductModelTest
```

Los tests verifican:
- Creación y validación de productos
- Gestión de stock
- Cálculos de inventario
- Predicciones de ML
- Endpoints de la API

## Características del Sistema

### Dashboard
- **Estadísticas en Tiempo Real**
  - Total de productos
  - Stock total
  - Movimientos del día
  - Productos en estado crítico

- **Gráficos Interactivos**
  - Tendencias de stock
  - Estado del inventario
  - Comparación stock actual vs predicción

### Sistema Predictivo
- Predicciones a 7 días
- Análisis de tendencias
  - Tendencia al alza
  - Tendencia estable
  - Tendencia a la baja
- Alertas predictivas
  - Stock crítico
  - Riesgo de agotamiento

### API REST

Documentación completa disponible en `/docs` o `/redoc`

#### Endpoints Principales:

- **Autenticación**:
```bash
POST /api/token/
# Obtener token de acceso
{
    "username": "usuario",
    "password": "contraseña"
}
```

- **Productos**:
```bash
GET /api/products/              # Listar todos los productos
POST /api/products/             # Crear nuevo producto
GET /api/products/{id}/         # Obtener producto específico
PUT /api/products/{id}/         # Actualizar producto
DELETE /api/products/{id}/      # Eliminar producto
```

- **Inventario**:
```bash
GET /api/inventory/movements/   # Listar movimientos
POST /api/inventory/movements/  # Crear movimiento
GET /api/inventory/stock/       # Ver stock actual
```

- **Predicciones**:
```bash
GET /api/products/{id}/predict  # Obtener predicciones de stock
```

Todos los endpoints (excepto autenticación) requieren un token válido en el header:
```bash
Authorization: Bearer {tu_token}
```

### Acceso al Panel de Administración

Para acceder al panel de administración de Django:

1. URL: `http://localhost:8001/admin`
2. Credenciales por defecto:
   - Usuario: `admin`
   - Contraseña: `Admin123!`

### Ejemplos de Operaciones Comunes

#### Actualizar Registros usando Django Shell

Para realizar actualizaciones masivas de registros, puedes usar el shell de Django. Aquí hay algunos ejemplos:

1. **Acceder al shell**:
```bash
# En instalación local
python manage.py shell

# Con Docker
docker-compose exec web python manage.py shell
```

2. **Ejemplo: Actualizar fechas de todos los movimientos**:
```python
# Importar módulos necesarios
from inventory.models import InventoryMovement
from datetime import datetime
import pytz

# Crear la fecha objetivo
target_date = datetime(2025, 6, 1, 10, 0, 0, tzinfo=pytz.UTC)

# Actualizar todos los registros
InventoryMovement.objects.all().update(date=target_date)

# Verificar la actualización
first_movement = InventoryMovement.objects.first()
print(f"ID: {first_movement.movement_id}, Fecha: {first_movement.date}")
```

3. **Otros ejemplos de actualizaciones masivas**:
```python
# Actualizar estado de productos
Product.objects.all().update(active=True)

# Actualizar stock de un producto específico
CurrentStock.objects.filter(product_id='P001').update(quantity=100)
```