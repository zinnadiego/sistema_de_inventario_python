# Usar una imagen base de Python
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para numpy/scipy/scikit-learn
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        python3-dev \
        libpq-dev \
        gfortran \
        musl-dev \
        libffi-dev \
        libssl-dev \
        libblas-dev \
        liblapack-dev \
        libatlas-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar setuptools primero y luego las dependencias de Python
RUN pip install --no-cache-dir setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Exponer el puerto
EXPOSE 8001

# Comando para ejecutar la aplicación
CMD ["uvicorn", "inventory_system.asgi:application", "--host", "0.0.0.0", "--port", "8001", "--reload"] 