from django.contrib import admin

# Register your models here.
from .models import DomainRecord, DnsRecord, RedirectRecord, Folder

admin.site.register(DomainRecord)
admin.site.register(DnsRecord)
admin.site.register(RedirectRecord)
admin.site.register(Folder)
