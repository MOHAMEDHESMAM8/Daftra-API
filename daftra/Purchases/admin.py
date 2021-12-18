from django.contrib import admin
from  .models import *
# Register your models here.
admin.site.register(PurchaseInvoice)
admin.site.register(PurchaseInvoice_products)
admin.site.register(PurchasePayments)

