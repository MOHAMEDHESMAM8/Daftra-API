from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(RolePermissions)
admin.site.register(Customers)
admin.site.register(Employees)
admin.site.register(Suppliers)
admin.site.register(Tax)
