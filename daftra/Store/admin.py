from django.contrib import admin
from  .models import *
# Register your models here.
admin.site.register(Warehouses)
admin.site.register(Products)
admin.site.register(Brands)
admin.site.register(Categories)
admin.site.register(ProductsCategory)
admin.site.register(AddPermissions)
admin.site.register(AddPermissions_Products)
admin.site.register(OutPermissions)
admin.site.register(OutPermissions_Products)

