from django.contrib import admin

# Register your models here.
from .models import DomainRecord

admin.site.register(DomainRecord)
