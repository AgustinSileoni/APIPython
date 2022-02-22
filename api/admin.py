from tokenize import group
from unicodedata import name
from django.contrib import admin
# Importamos nuestros modelos
from api import models, constants
#Importarmos el modelo de Group
from django.contrib.auth.models import Group
#Importamos el error que no se pudo hacer la operacion
from django.db.utils import OperationalError

# Register your models here.
admin.site.register(models.Account)
admin.site.register(models.Transaction)

#Creamos el grupo de ADMIN
try:
        group, created = Group.objects.get_or_create(name=constants.GROUP_ADMIN)
        if created:
            print("Admin creado exitosamente")
        else:
            print("Admin ya existía, no fue creado")
        #Creamos el grupo de USER
        group, created = Group.objects.get_or_create(name=constants.GROUP_USER)
        if created:
            print("User creado exitosamente")
        else:
            print("User ya existía, no fue creado")
except OperationalError:
	    print("No existe la base de datos de los grupos")