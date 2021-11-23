from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('allInvoices', csrf_exempt(get_all_invoice), name='allInvoices'),
    path('create', createSaleInvoice.as_view(), name='createinvoice'),
    path('update/<int:id>', updateSaleInvoice.as_view(), name='update'),
    path('InvoicePayments/invoice=<int:invoice>', ShowPayments.as_view(), name='allPayments'),
    path('PaymentDetails/payment=<int:payment>', PaymentDetails.as_view(), name='paymentDetail'),
    path('PaymentCreate', PaymentCreate.as_view(), name='PaymentCreate'),
    path('InvoiceStore/Invoice=<int:invoice>', InvoiceStore.as_view(), name='InvoiceStore'),
    path('RecordHistory/<int:invoice>', csrf_exempt(get_invoice_recordhistory), name='recordHistory'),
    path('InvoiceStore/<int:invoice>', csrf_exempt(get_invoice_store), name='store'),

]
