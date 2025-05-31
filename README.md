# Sistema de Inventario

Este proyecto es un sistema de gestión de inventario que combina Django y FastAPI para proporcionar una robusta aplicación web con una API RESTful y capacidades predictivas de stock.

## Características Principales

- **Dashboard en Tiempo Real**: Visualización de estadísticas clave y estado del inventario
- **Predicciones Inteligentes**: Sistema predictivo que analiza tendencias de stock
- **Alertas Automáticas**: Notificaciones de stock crítico y tendencias negativas
- **API REST Completa**: Endpoints para todas las operaciones de inventario
- **Interfaz Moderna**: UI/UX optimizada con gráficos interactivos
- **Sistema de Roles**: Control de acceso basado en roles

## Tecnologías Utilizadas

### Backend
- Django 5.0.1
- FastAPI 0.109.0
- PostgreSQL (Base de datos)
- Scikit-learn (Predicciones)
- Pandas (Análisis de datos)

### Frontend
- Bootstrap 5
- Chart.js (Gráficos)
- Font Awesome (Iconos)

## Instalación con Docker (Recomendado)

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

El sistema estará disponible en `http://localhost:8001`

## Instalación Manual

1. **Clonar el repositorio y crear entorno virtual**:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar la base de datos**:
- Crear una base de datos PostgreSQL
- Copiar `.env.example` a `.env` y configurar las variables

4. **Aplicar migraciones**:
```bash
python manage.py migrate
```

5. **Crear superusuario**:
```bash
python create_superuser.py
```

6. **Cargar datos de ejemplo**:
```bash
python manage.py load_sample_data
```

7. **Iniciar el servidor**:
```bash
python manage.py runserver 8001
```

## Estructura del Proyecto

```
├── api/                 # Endpoints FastAPI
├── inventory/           # App principal Django
│   ├── management/     # Comandos personalizados
│   ├── migrations/     # Migraciones DB
│   ├── models.py       # Modelos de datos
│   └── views.py        # Vistas Django
├── templates/          # Plantillas HTML
├── static/             # Archivos estáticos
└── docker/             # Configuración Docker
```

## Datos de Ejemplo

El sistema incluye un comando para cargar datos de ejemplo que incluye:
- Productos de tecnología con diferentes categorías
- Histórico de movimientos
- Predicciones iniciales
- Umbrales de stock configurados

Para cargar los datos:
```bash
python manage.py load_sample_data
```

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
  POST /api/token
  ```

- **Productos**:
  ```bash
  GET /api/products
  POST /api/products
  GET /api/products/{id}
  ```

- **Stock**:
  ```bash
  GET /api/inventory/stock
  POST /api/inventory/movements
  ```

- **Predicciones**:
  ```bash
  GET /api/products/{id}/predict
  ```

## Credenciales por Defecto

- **Admin**:
  - Usuario: admin2
  - Contraseña: admin123
