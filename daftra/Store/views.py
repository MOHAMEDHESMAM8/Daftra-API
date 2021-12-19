from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

import json
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from Sales.models import *
from Users.models import RecordHistory
from datetime import datetime, timedelta
from django.db.models import Q, Exists, OuterRef
from .permissions import IsEmployee, RolesPermissionsCheck


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_product_store(request, product):
    RolesPermissionsCheck(request, "can_show_products")

    products = SaleInvoice_products.objects.filter(product_id=product)
    data = []
    for item in products:
        obj = {
            "invoice_id": item.sales_invoice.id,
            "created_at": item.sales_invoice.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
            "warehouse": item.sales_invoice.warehouse.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "count_after": item.count_after,
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


# TODO add and update have same data in here and invoice (mabye table for sold and update)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_product_recordhistory(request, product):
    events = RecordHistory.objects.filter(product_id=product)
    data = []
    for item in events:
        if item.type == 'sold_product' or item.type == 'update_product_invoice':
            try:
                data_obj = SaleInvoice_products.objects.get(pk=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "invoice_id": data_obj.sales_invoice.id,
                    "product_id": data_obj.product.id,
                    "product_name": data_obj.product.name,
                    "unit_price": data_obj.unit_price,
                    "items": data_obj.quantity,
                    "store": data_obj.count_after
                }
            except ObjectDoesNotExist:
                data_obj = deletedActivities.objects.get(product=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "invoice_id": item.sales_invoice,
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "unit_price": data_obj.amount,
                    "items": data_obj.item_count,
                    "store": data_obj.store_count
                }
            data.append(obj)
        if item.type == 'update_product':
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "id": item.product.id,
                "name": item.product.name,
                "selling_price": item.product.selling_price,
            }
            data.append(obj)
        if item.type == 'update_product_addPermission' or item.type == 'add_product_addPermission':
            try:
                product = AddPermissions_Products.objects.get(id=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "id": item.addPermissions.id,
                    "product_name": item.product.name,
                    "product_id": item.product.id,
                    "unit_price": product.unit_price,
                    "quantity": product.quantity,
                    "count_after": product.count_after,
                }
            except ObjectDoesNotExist:
                data_obj = deletedActivities.objects.get(product=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "id": item.addPermissions.id,
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "unit_price": data_obj.amount,
                    "items": data_obj.item_count,
                    "store": data_obj.store_count
                }
            data.append(obj)
        if item.type == 'update_product_outPermission' or item.type == 'add_product_outPermission':
            try:
                product = OutPermissions_Products.objects.get(id=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "id": item.outPermissions.id,
                    "product_name": item.product.name,
                    "product_id": item.product.id,
                    "unit_price": product.unit_price,
                    "quantity": product.quantity,
                    "count_after": product.count_after,
                }
            except ObjectDoesNotExist:
                data_obj = deletedActivities.objects.get(product=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "id": item.outPermissions.id,
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "unit_price": data_obj.amount,
                    "items": data_obj.item_count,
                    "store": data_obj.store_count
                }
            data.append(obj)
        if item.type == 'delete_product_addPermission':
            print(data)
            data_obj = deletedActivities.objects.get(id=item.activity_id)
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "id": item.addPermissions.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "unit_price": data_obj.amount,
                "items": data_obj.item_count,
                "store": data_obj.store_count
            }
            data.append(obj)
        if item.type == 'delete_product_outPermission':
            data_obj = deletedActivities.objects.get(id=item.activity_id)
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "id": item.outPermissions.id,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "unit_price": data_obj.amount,
                "items": data_obj.item_count,
                "store": data_obj.store_count
            }
            data.append(obj)
        if item.type == 'delete_product_invoice':
            data_obj = deletedActivities.objects.get(product=item.activity_id)
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "invoice_id": item.sales_invoice,
                "product_id": item.product.id,
                "product_name": item.product.name,
                "unit_price": data_obj.amount,
                "items": data_obj.item_count,
                "store": data_obj.store_count
            }
            data.append(obj)

    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


# get percentage last month
def get_month(product):
    month = datetime.today().month
    sold = SaleInvoice.objects.filter(created_at__month=month)
    current_count = 0
    for item in sold:
        try:
            obj = item.SaleInvoice_products.get(product_id=product)
        except ObjectDoesNotExist:
            continue
        current_count += obj.quantity

    last_count = 0
    sold_last = SaleInvoice.objects.filter(created_at__month=month - 1)
    for item in sold_last:
        try:
            obj = item.SaleInvoice_products.get(product_id=product)
        except ObjectDoesNotExist:
            continue
        last_count += obj.quantity

    if current_count > last_count:
        try:
            sub = current_count - last_count
            output = (sub / last_count) * 100
        except ZeroDivisionError:
            sub = 0
            output = 0
        obj = {
            "sub": sub,
            'output': output,
            "current": current_count,
            "sign": "+"
        }
        return obj
    else:
        try:
            sub = last_count - current_count
            output = (sub / current_count) * 100
        except ZeroDivisionError:
            sub = 0
            output = 0
        obj = {
            "sub": sub,
            'output': output,
            "current": current_count,
            "sign": "-"
        }
        return obj


# get percentage last 7 days
def get_last_7_days(product):
    days = datetime.now() - timedelta(days=7)
    sold = SaleInvoice.objects.filter(created_at__gte=days)
    days14 = datetime.now() - timedelta(days=14)
    sold_last = SaleInvoice.objects.filter(
        ~Exists(SaleInvoice.objects.filter(id=OuterRef('id'), created_at__gte=days)),
        created_at__gte=days14)

    current_count = 0
    for item in sold:
        try:
            obj = item.SaleInvoice_products.get(product_id=product)
        except ObjectDoesNotExist:
            continue
        current_count += obj.quantity

    last_count = 0

    for item in sold_last:
        try:
            obj = item.SaleInvoice_products.get(product_id=product)
        except ObjectDoesNotExist:
            continue
        last_count += obj.quantity

    if current_count > last_count:
        try:
            sub = current_count - last_count
            output = (sub / last_count) * 100
        except ZeroDivisionError:
            sub = 0
            output = 0
        obj = {
            "sub": sub,
            'output': output,
            "current": current_count,
            "sign": "+"
        }
        return obj
    else:
        try:
            sub = last_count - current_count
            output = (sub / current_count) * 100
        except ZeroDivisionError:
            sub = 0
            output = 0
        obj = {
            "sub": sub,
            'output': output,
            "current": current_count,
            "sign": "-"
        }
        return obj


class GetProducts(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        products = Products.objects.all()
        data = []
        for item in products:
            obj = {
                "name": item.name,
                "id": item.id,
                'status': item.product_count_status(product=item.id),
                'count': item.product_count(product=item.id),
                "purchasing_price": item.purchasing_price,
                "selling_price": item.selling_price,
                "deactivate": item.deactivate,
                "barcode": item.barcode,
                "brand": item.brand.name,
            }
            data.append(obj)
        json_format = json.dumps(data)
        return HttpResponse(json_format, content_type='application/json; charset=utf-8')


# TODO change average to buy not sale
class ProductDetails(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, product):
        data = {}

        # det count on store
        products = Product_count.objects.filter(product_id=product)
        objs = []
        for item in products:
            obj = {
                "warehouse_name": item.warehouse.name,
                "count": item.count,
                "barcode": item.barcode,
            }
            objs.append(obj)
        data["Stock Quantity"] = objs

        # count sold quantity & average price
        soldproducts = 0
        price = 0
        sold = SaleInvoice_products.objects.filter(product_id=product)
        for item in sold:
            soldproducts += item.quantity
            price += item.unit_price
        data["Total sold"] = soldproducts
        data["average price"] = price / sold.count()
        data["month_solds"] = get_month(product)
        data["7_days_solds"] = get_last_7_days(product)
        json_format = json.dumps(data)
        return HttpResponse(json_format, content_type='application/json; charset=utf-8')


class CreateProduct(APIView):
    # permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        products = Products.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        RolesPermissionsCheck(request, "can_add_product")

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProduct(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, product):
        product = Products.objects.get(id=product)
        serializer = ProductSerializer(product)
        obj = serializer.data
        obj["supplier_name"] = product.supplier.user.first_name + " " + product.supplier.user.last_name

        return Response(obj, status=status.HTTP_200_OK)

    def put(self, request, product):
        RolesPermissionsCheck(request, "can_edit_Or_delete_products")
        product = Products.objects.get(id=product)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=product, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product):
        RolesPermissionsCheck(request, "can_edit_Or_delete_products")
        product = Products.objects.get(id=product)
        product.delete()
        return Response("done", status=status.HTTP_204_NO_CONTENT)


class getCreateBrand(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        objects = Brands.objects.all()
        serializer = BrandSerializer(objects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteBrand(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, brand):
        obj = Brands.objects.get(id=brand)
        serializer = BrandSerializer(obj)
        return Response(serializer.data)

    def put(self, request, brand):
        obj = Brands.objects.get(id=brand)
        serializer = BrandSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, brand):
        obj = Brands.objects.get(id=brand)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class getCreateCategory(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        objects = Categories.objects.all()
        serializer = CategorySerializer(objects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteCategory(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, category):
        obj = Categories.objects.get(id=category)
        serializer = CategorySerializer(obj)
        return Response(serializer.data)

    def put(self, request, category):
        obj = Categories.objects.get(id=category)
        serializer = CategorySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, category):
        obj = Categories.objects.get(id=category)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AllPermissions(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        RolesPermissionsCheck(request, "can_show_storePermissions")
        out = OutPermissions.objects.all()
        add = AddPermissions.objects.all()
        data = []
        for item in out:
            obj = {
                "type": 'outPermission',
                "id": item.id,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "add_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "notes": item.notes,
            }
            data.append(obj)
        for item in add:
            obj = {
                "type": 'addPermission',
                "id": item.id,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "add_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "notes": item.notes,
            }
            data.append(obj)
        final = json.dumps(data)
        return HttpResponse(final, content_type='application/json; charset=utf-8')


class CreateOutPermission(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        products = OutPermissions.objects.all()
        serializer = OutPermissionsSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        RolesPermissionsCheck(request, "can_add_storePermission")
        serializer = OutPermissionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data, user=request.user.employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateAddPermission(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        products = AddPermissions.objects.all()
        serializer = AddPermissionsSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        RolesPermissionsCheck(request, "can_add_storePermission")
        serializer = AddPermissionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data, user=request.user.employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateOutPermission(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, permission):
        products = OutPermissions.objects.get(id=permission)
        serializer = OutPermissionsSerializer(products)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, permission):
        RolesPermissionsCheck(request, "can_edit_Or_delete_storePermission")
        product = OutPermissions.objects.get(id=permission)
        serializer = OutPermissionsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=product, validated_data=request.data, user=request.user.employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, permission):
        RolesPermissionsCheck(request, "can_edit_Or_delete_storePermission")
        permission_obj = OutPermissions.objects.get(id=permission)
        for item in permission_obj.OutPermissions_Products.all():
            # change product count
            product_count(operation="+", product=item.product, quantity=item.quantity,
                          warehouse=item.out_permission.warehouse)
            # add delete record
            deleted_product = deletedActivities.objects.create(
                item_count=item.quantity,
                store_count=item.quantity + item.count_after,
                amount=item.unit_price,
                product=item.product.id
            )
            # add record history
            add_record_history(activity_type="delete_product_outPermission",
                               add_by=item.out_permission.add_by,
                               activity_id=deleted_product.id,
                               product=item.product,
                               outpermissions=permission_obj
                               )
        permission_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateAddPermission(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, permission):
        products = AddPermissions.objects.get(id=permission)
        serializer = AddPermissionsSerializer(products)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, permission):
        RolesPermissionsCheck(request, "can_edit_Or_delete_storePermission")
        product = AddPermissions.objects.get(id=permission)
        serializer = AddPermissionsSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=product, validated_data=request.data, user=request.user.employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, permission):
        RolesPermissionsCheck(request, "can_edit_Or_delete_storePermission")
        permission_obj = AddPermissions.objects.get(id=permission)
        for item in permission_obj.AddPermissions_Products.all():
            # change product count
            product_count(operation="+", product=item.product, quantity=item.quantity,
                          warehouse=item.add_permission.warehouse)
            # add delete record
            deleted_product = deletedActivities.objects.create(
                item_count=item.quantity,
                store_count=item.quantity + item.count_after,
                amount=item.unit_price,
                product=item.product.id
            )
            # add record history
            add_record_history(activity_type="delete_product_addPermission",
                               add_by=item.add_permission.add_by,
                               activity_id=deleted_product.id,
                               product=item.product,
                               addpermissions=permission_obj
                               )
        permission_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_add_permissions_recordhistory(request, addpermission):
    events = RecordHistory.objects.filter(addPermissions_id=addpermission)
    data = []

    for item in events:
        if item.type == 'add_addPermission' or item.type == 'update_addPermission':
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "id": item.addPermissions.id,
            }
            data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_out_permissions_recordhistory(request, outpermission):
    events = RecordHistory.objects.filter(outPermissions_id=outpermission)
    data = []

    for item in events:
        if item.type == 'add_outPermission' or item.type == 'update_outPermission':
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "id": item.outPermissions.id,
            }
            data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')
