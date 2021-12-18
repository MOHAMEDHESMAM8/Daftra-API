from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(SaleInvoice)
admin.site.register(SalePayments)
admin.site.register(SaleInvoice_products)
