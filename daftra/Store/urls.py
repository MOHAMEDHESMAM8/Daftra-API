from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    # path('allInvoices', csrf_exempt(get_all_invoice), name='allInvoices'),
    path('allProducts', GetProducts.as_view(), name='products'),
    path('ProductDetails/<int:product>', ProductDetails.as_view(), name='ProductDetails'),
    path('ProductStore/<int:product>', csrf_exempt(get_product_store), name='store'),
    path('RecordHistory/<int:product>', csrf_exempt(get_product_recordhistory), name='record history'),
    path('CreateProduct', CreateProduct.as_view(), name='create'),
    path('UpdateProduct/<int:product>', UpdateProduct.as_view(), name='update'),
    path('AllPermissions', AllPermissions.as_view(), name='all'),
    path('CreateOutPermission', CreateOutPermission.as_view(), name='create'),
    path('CreateAddPermission', CreateAddPermission.as_view(), name='create'),
    path('UpdateOutPermission/<int:permission>', UpdateOutPermission.as_view(), name='update'),
    path('UpdateAddPermission/<int:permission>', UpdateAddPermission.as_view(), name='update'),
    path('RecordHistory/<int:addpermission>', csrf_exempt(get_add_permissions_recordhistory), name='record history'),
    path('RecordHistory/<int:outpermission>', csrf_exempt(get_out_permissions_recordhistory), name='record history'),

]

