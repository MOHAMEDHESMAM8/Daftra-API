from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('allInvoices', csrf_exempt(get_all_invoice), name='allInvoices'),
    path('create', createPurchaseInvoice.as_view(), name='create invoice'),
    path('update/<int:invoice>', updatePurchaseInvoice.as_view(), name='update invoice'),
    path('InvoicePayments/<int:invoice>', ShowPayments.as_view(), name='allPayments'),
    path('PaymentDetails/<int:payment>', PaymentDetails.as_view(), name='paymentDetail'),
    path('PaymentCreate', PaymentCreate.as_view(), name='PaymentCreate'),
    path('InvoiceStore/<int:invoice>', InvoiceStore.as_view(), name='InvoiceStore'),
    path('RecordHistory/<int:invoice>', csrf_exempt(get_invoice_recordhistory), name='recordHistory'),
    path('allSupplierList', csrf_exempt(get_all_supplier), name='all supplier list'),

]

