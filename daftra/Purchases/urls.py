from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('allInvoices', csrf_exempt(get_all_invoice), name='allInvoices'),
    path('create', createPurchaseInvoice.as_view(), name='create invoice'),
    path('update/<int:invoice>', updatePurchaseInvoice.as_view(), name='update invoice'),

]

