from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    # path('allInvoices', csrf_exempt(get_all_invoice), name='allInvoices'),
    path('allProducts', GetProducts.as_view(), name='products'),
    path('ProductDetails/product=<int:product>', ProductDetails.as_view(), name='ProductDetails'),
    path('ProductStore/product=<int:product>', csrf_exempt(get_product_store), name='store'),
    path('RecordHistory/product=<int:product>', csrf_exempt(get_product_recordhistory), name='record history'),
    path('CreateProduct', CreateProduct.as_view(), name='create'),
    path('UpdateProduct/product=<int:product>', UpdateProduct.as_view(), name='update'),
    path('AllPermissions', AllPermissions.as_view(), name='all'),
    path('CreateOutPermission', CreateOutPermission.as_view(), name='create'),
    path('CreateAddPermission', CreateAddPermission.as_view(), name='create'),
    path('UpdateOutPermission/permission=<int:permission>', UpdateOutPermission.as_view(), name='update'),
    path('UpdateAddPermission/permission=<int:permission>', UpdateAddPermission.as_view(), name='update'),
    path('RecordHistory/addpermission=<int:addpermission>', csrf_exempt(get_add_permissions_recordhistory), name='record history'),
    path('RecordHistory/outpermission=<int:outpermission>', csrf_exempt(get_out_permissions_recordhistory), name='record history'),

]

