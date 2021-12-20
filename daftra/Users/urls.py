from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view()),
    path('logout/blacklist/', BlacklistTokenUpdateView.as_view(),
         name='blacklist'),
    path('SupplierCreate', GetCreateSupplier.as_view(), name='getall create'),
    path('SupplierUpdate/<int:supplier>', GetUpdateDeleteSupplier.as_view(), name=' get update delete'),
    path('SupplierPurchase/<int:supplier>', GetSupplierPurchases.as_view(), name=' get'),
    path('Customers', GetCreateCustomers.as_view(), name=' get create customers'),
    path('CustomerDetails/<int:customer>', GetCustomerDetails.as_view(), name='customer details'),
    path('allInvoicesCustomer/<int:customer>', csrf_exempt(get_all_invoice_customer), name='allInvoices'),
    path('getPaymentsCustomer/<int:customer>', csrf_exempt(get_all_Payment_customer), name='allInvoices'),
    path('Employees', GetCreateEmployees.as_view(), name=' get create employees'),
    path('UpdateEmployee/<int:employee>', UpdateDeleteEmployees.as_view(), name=' get update delete employee'),
    path('Tax', GetCreateTaxs.as_view(), name=' get create tax'),
    path('UpdateTax/<int:tax>', UpdateDeleteTax.as_view(), name=' get update delete tax'),
    path('Roles', GetCreateRoles.as_view(), name=' get create role'),
    path('UpdateRole/<int:role>', UpdateDeleteRole.as_view(), name=' get update delete Roles'),
    path('getNotesAction/<str:type>', GetNotesActions.as_view(), name=' get notes actions'),
    path('NotesActionDetails/<int:note>', GetUpdateDeleteNotesActions.as_view(), name=' get update delete notes actions'),
    path('create', CreateNotesActions.as_view(), name=' create notes actions'),
    path('getNotes/<str:type>', GetNotes.as_view(), name=' get notes'),
    path('NotesDetails/<int:note>', GetUpdateDeleteNotes.as_view(), name=' get update delete notes'),
    path('create', CreateNotes.as_view(), name=' create notes'),
]
