"""
URL configuration for inventory_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import HttpResponse
from api.main import app as fastapi_app
from fastapi.staticfiles import StaticFiles

# Mount FastAPI
app = fastapi_app

urlpatterns = [
    path('', include('inventory.urls')),
    path('admin/', admin.site.urls),
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
    # Redirigir todas las rutas que empiecen con /api/ a FastAPI
    re_path(r'^api/.*$', lambda request: HttpResponse(status=404)),  # Placeholder para FastAPI
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
