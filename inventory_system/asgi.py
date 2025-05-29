"""
ASGI config for inventory_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.main import app as fastapi_app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django_app = get_asgi_application()

async def application(scope, receive, send):
    if scope["type"] == "http":
        path = scope["path"]
        # Rutas que deben ser manejadas por FastAPI
        if path.startswith(("/api/", "/docs", "/openapi.json", "/redoc")):
            return await fastapi_app(scope, receive, send)
        # Para todas las demás rutas, usar Django
        return await django_app(scope, receive, send)
    return await django_app(scope, receive, send)
