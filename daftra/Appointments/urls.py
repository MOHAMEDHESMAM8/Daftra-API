from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [

    path('getCreateAppointments', getCreateAppointments.as_view(), name='get create'),
    # path('allInvoicesCustomer/<int:customer>', csrf_exempt(get_all_invoice_customer), name='allInvoices'),

]
