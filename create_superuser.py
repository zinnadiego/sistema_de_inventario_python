import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from django.contrib.auth.models import User, Group

# Crear o actualizar el superusuario
try:
    user = User.objects.get(username='admin')
    user.set_password('Admin123!')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Usuario admin actualizado correctamente")
except User.DoesNotExist:
    User.objects.create_superuser('admin', 'admin@example.com', 'Admin123!')
    print("Usuario admin creado correctamente")

# Crear grupos si no existen
admin_group, _ = Group.objects.get_or_create(name='Administrador')
read_group, _ = Group.objects.get_or_create(name='Lectura')
print("Grupos creados/verificados correctamente") 