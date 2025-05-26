# Sistema de Inventario

Este proyecto es un sistema de gestión de inventario que combina Django y FastAPI para proporcionar una robusta aplicación web con una API RESTful.

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

### Base de Datos
- **PostgreSQL** (a través de psycopg2-binary): Sistema de gestión de base de datos relacional

## Manual de Instalación y Uso

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Instalar las dependencias:
```bash
py -m pip install -r requirements.txt
```

3. Configurar la base de datos:
```bash
py manage.py migrate
```

4. Crear un superusuario para acceder al panel de administración:
```bash
py manage.py createsuperuser
```

### Ejecutar el Proyecto

Para iniciar el servidor de desarrollo:
```bash
py -m uvicorn inventory_system.asgi:application --reload
```

El proyecto estará disponible en:
- Interfaz web: http://127.0.0.1:8000
- Panel de administración: http://127.0.0.1:8000/admin
- Documentación de la API: http://127.0.0.1:8000/api/docs

## Caso de Uso Práctico

### Gestión de Productos en el Inventario

1. **Acceso al Sistema**
   - Acceder al panel de administración en http://127.0.0.1:8000/admin
   - Iniciar sesión con las credenciales del superusuario

2. **Gestión vía Panel de Administración**
   - Navegar a la sección "Products"
   - Agregar, editar o eliminar productos
   - Gestionar el stock actual
   - Ver movimientos de inventario

3. **Uso de la API REST**
   - Obtener token de autenticación:
     ```bash
     curl -X POST "http://127.0.0.1:8000/api/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=tu_usuario&password=tu_contraseña"
     ```

   - Listar productos:
     ```bash
     curl -X GET "http://127.0.0.1:8000/api/products/" -H "Authorization: Bearer tu_token"
     ```

   - Crear nuevo producto:
     ```bash
     curl -X POST "http://127.0.0.1:8000/api/products/" \
     -H "Authorization: Bearer tu_token" \
     -H "Content-Type: application/json" \
     -d '{
         "product_id": "PRD001",
         "product_name": "Laptop",
         "sku": "LAP-001",
         "unit_of_measure": "unidad",
         "cost": 800.00,
         "sale_price": 1200.00,
         "category": "Electronics",
         "location": "Warehouse A"
     }'
     ```

### Características Principales
- Gestión completa de productos (CRUD)
- Control de stock en tiempo real
- API REST documentada con Swagger UI
- Panel de administración intuitivo
- Sistema de autenticación seguro

## Notas Adicionales
- La documentación completa de la API está disponible en `/api/docs`
- El sistema utiliza autenticación JWT para la API
- Todas las operaciones de la API requieren autenticación
- Los endpoints están protegidos y requieren tokens válidos

## Próximas Funcionalidades
- Integración con machine learning para predicción de stock (pendiente de implementar)
- Reportes y análisis avanzados
- Dashboard con métricas en tiempo real 