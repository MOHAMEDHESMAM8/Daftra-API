from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [

    path('getCreateAppointments', getCreateAppointments.as_view(), name='get create'),
    path('GetUpdateDeleteAppointments/<int:appointment>', GetUpdateDeleteAppointments.as_view(), name='get update delete'),
    path('getCreateActions', getCreateAppointmentsActions.as_view(), name='get create'),
    path('GetUpdateDeleteActions/<int:action>', GetUpdateDeleteAppointmentsActions.as_view(), name='get update delete'),
    # path('allInvoicesCustomer/<int:customer>', csrf_exempt(get_all_invoice_customer), name='allInvoices'),

]
