from django.contrib import admin
# Importamos nuestros modelos
from api import models

# Register your models here.
admin.site.register(models.Account)