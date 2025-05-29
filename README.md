# Sistema de Inventario

Este proyecto es un sistema de gestión de inventario que combina Django y FastAPI para proporcionar una robusta aplicación web con una API RESTful y capacidades predictivas de stock.

## Tecnologías y Librerías Utilizadas

### Backend
- **Django (5.0.1)**: Framework web principal para el manejo del panel de administración y la interfaz web
- **FastAPI (0.109.0)**: Framework moderno para la API REST con soporte para operaciones asíncronas
- **Uvicorn (0.27.0)**: Servidor ASGI para ejecutar tanto Django como FastAPI
- **SQLAlchemy (2.0.25)**: ORM utilizado por FastAPI para interactuar con la base de datos
- **Python-Jose (3.3.0)**: Para el manejo de tokens JWT en la autenticación
- **Passlib (1.7.4)**: Para el manejo seguro de contraseñas
- **Python-Multipart (0.0.8)**: Para el manejo de formularios y archivos en FastAPI
- **Python-dotenv (1.0.0)**: Para la gestión de variables de entorno
- **Scikit-learn**: Para el análisis predictivo de stock
- **Pandas**: Para el procesamiento de datos históricos

### Base de Datos
- **PostgreSQL** (a través de psycopg2-binary): Sistema de gestión de base de datos relacional

## Sistema de Roles y Permisos

El sistema implementa un modelo de permisos simplificado con dos roles principales:

### Roles Disponibles
- **Administrador**: Acceso completo al sistema con capacidad de gestión
  - Puede crear/editar/eliminar productos
  - Puede gestionar usuarios
  - Acceso total al panel de administración
  - Puede ver y modificar todos los módulos

- **Lectura**: Acceso limitado para visualización
  - Puede ver productos y su estado
  - Acceso de solo lectura a los módulos
  - No puede realizar modificaciones

## Manual de Instalación y Uso

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Unix o MacOS:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la base de datos:
```bash
# Crear la base de datos
python manage.py migrate

# Crear superusuario
python create_superuser.py

# Cargar datos iniciales (opcional)
python load_initial_data.py
```

5. Iniciar el servidor:
```bash
python manage.py runserver
```

El sistema estará disponible en `http://127.0.0.1:8001/`

## Estructura del Proyecto

- `api/`: Endpoints de la API REST
- `inventory/`: Aplicación principal de gestión de inventario
- `templates/`: Plantillas HTML
- `static/`: Archivos estáticos (CSS, JS, imágenes)
- `migrations/`: Migraciones de la base de datos

## Base de Datos

El proyecto utiliza SQLite por defecto. Las migraciones están incluidas en el repositorio.

Para resetear la base de datos:
1. Eliminar `db.sqlite3` si existe
2. Ejecutar `python manage.py migrate`
3. Ejecutar `python create_superuser.py`
4. Opcionalmente, ejecutar `python load_initial_data.py`

## Desarrollo

Para crear nuevas migraciones después de cambios en los modelos:
```bash
python manage.py makemigrations
python manage.py migrate
```


## API REST

La API está organizada en las siguientes categorías:

### 1. Autenticación
- **POST /api/token** - Iniciar sesión y obtener token
  ```bash
  curl -X POST "http://localhost:8001/api/token" \
       -H "Content-Type: application/x-www-form-urlencoded" \
       -d "username=usuario&password=contraseña"
  ```

### 2. Productos
- **GET /api/products/** - Listar productos
- **POST /api/products/** - Crear producto
- **GET /api/products/{product_id}** - Obtener producto
- **PUT /api/products/{product_id}** - Actualizar producto

### 3. Predicción
- **GET /api/products/{product_id}/predict** - Predecir stock
  - Parámetros opcionales:
    - days: Número de días para la predicción (default: 7)

### 4. Usuarios
- **POST /api/users/** - Crear usuario
- **PUT /api/users/{user_id}** - Actualizar usuario
- **DELETE /api/users/{user_id}** - Eliminar usuario

### 5. Inventario
- **POST /api/inventory/movements/** - Crear movimiento
- **GET /api/inventory/movements/** - Listar movimientos
  - Filtros disponibles:
    - product_id
    - movement_type (entrada/salida)
    - start_date
    - end_date
- **POST /api/inventory/stock/{product_id}/add** - Agregar stock
- **POST /api/inventory/stock/{product_id}/remove** - Remover stock
- **GET /api/inventory/stock/** - Obtener stock actual

## Características del Sistema

### Control de Inventario
- Gestión completa de productos (CRUD)
- Registro de movimientos (entradas/salidas)
- Control de stock en tiempo real
- Alertas de stock bajo
- Histórico de movimientos

### Sistema Predictivo
- Predicciones de stock a 7 días
- Análisis de tendencias
- Indicadores de rendimiento
- Alertas predictivas

### Seguridad
- Autenticación mediante tokens
- Sistema de roles y permisos
- Protección de endpoints
- Validación de datos

### Monitoreo
- Dashboard en tiempo real
- Estadísticas de movimientos
- Reportes de stock
- Alertas y notificaciones
