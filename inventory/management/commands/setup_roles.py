from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import ContentType
from django.contrib.admin.models import LogEntry

class Command(BaseCommand):
    help = 'Configura los roles básicos del sistema'

    def handle(self, *args, **kwargs):
        # Limpiar grupos existentes
        Group.objects.all().delete()

        # Crear grupo Administrador
        admin_group = Group.objects.create(name='Administrador')
        
        # Obtener todos los permisos disponibles
        all_permissions = Permission.objects.all()
        
        # Asignar todos los permisos al grupo Administrador
        admin_group.permissions.set(all_permissions)

        # Crear grupo Lectura
        read_group = Group.objects.create(name='Lectura')
        
        # Obtener los permisos de lectura (view)
        view_permissions = Permission.objects.filter(codename__startswith='view_')
        
        # Asignar permisos de lectura al grupo Lectura
        read_group.permissions.set(view_permissions)

        self.stdout.write(self.style.SUCCESS('Roles configurados exitosamente')) 