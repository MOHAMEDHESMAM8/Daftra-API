from django.http import HttpResponse

import json
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import RolesPermissionsCheck, IsEmployee
from .serializers import *
from Users.models import RecordHistory
import json


# update Invoice paid status
def update_invoice_status(invoice, current=0, update=0):
    obj = SaleInvoice.objects.get(pk=invoice)
    payments = obj.SalePayments.all()
    sum = int(current)
    for item in payments:
        if item.id == update:
            continue
        sum += item.Amount
    if obj.total == sum:
        obj.paid = True
        obj.save()
        return "done"
    elif obj.total > sum:
        obj.paid = False
        obj.save()
        return "done"
    else:
        return "error"


# todo remove old file after update form files
def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_invoice(request):
    with connection.cursor() as cursor:
        if request.user.employee.role.can_show_saleBills:
            cursor.execute("""SELECT
                 invoice.id,
                 DATE_FORMAT(invoice.created_at, "%d-%m-%Y %H:%m") as created_at_invoice,
                 invoice.total,
                 invoice.paid,
                 invoice.customer as customer_id,
                 user.first_name as customer_name
                 FROM
                     sales_saleinvoice AS invoice
                 INNER JOIN users_customers AS customer
                 ON
                     invoice.customer = customer.id
                 INNER JOIN users_user AS user
                 ON
                 user.id = customer.user
                 """)
        elif request.user.employee.role.can_show_his_saleBills:
            n = request.user.employee.id
            query = f"""SELECT
                            invoice.id,
                            DATE_FORMAT(invoice.created_at, "%d-%m-%Y %H:%m") as created_at_invoice,
                            invoice.total,
                            invoice.paid,
                            invoice.customer as customer_id,
                            user.first_name as customer_name
                            FROM
                                sales_saleinvoice AS invoice
                            INNER JOIN users_customers AS customer
                            ON
                                invoice.customer = customer.id
                            INNER JOIN users_user AS user
                            ON
                            user.id = customer.user
                            where invoice.sold_by = {n} """
            cursor.execute(query)
        else:
            r = RolesPermissionsCheck(request, "can_show_saleBills")
            r.has_permission()

        json_format = json.dumps(dictfetchall(cursor))
        data = json.loads(json_format)
        for item in data:
            invoice = item.get("id")
            record = RecordHistory.objects.filter(sale=invoice).latest("id")
            item["last_activaty"] = record.type
            item['created_at'] = record.created_at.strftime("%m/%d/%Y, %H:%M:%S")
        final = json.dumps(data)
        cursor.close()
    return HttpResponse(final, content_type='application/json; charset=utf-8')


# todo  check from front upload photo is working
class createSaleInvoice(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request):
        invoices = SaleInvoice.objects.all()
        serializer = SaleInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        r = RolesPermissionsCheck(request, "can_add_saleBill")
        r.has_permission()
        serializer = SaleInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            invoice = serializer.create(validated_data=request.data, user=request.user.employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# todo  check from front upload photo is working
class updateSaleInvoice(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request, id):
        invoice = SaleInvoice.objects.get(pk=id)
        serializer = SaleInvoiceSerializer(invoice)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_saleBill")
        r.has_permission()
        invoice = SaleInvoice.objects.get(pk=id)
        serializer = SaleInvoiceSerializer(invoice, request.data)
        if serializer.is_valid():
            serializer.update(instance=invoice, validated_data=request.data)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowPayments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    def get(self, request, invoice):

        payments = SaleInvoice.objects.get(pk=invoice)
        serializer = paymentsInvoiceSerializer(payments)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentDetails(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, payment):
        payments = SalePayments.objects.get(pk=payment)
        serializer = paymentDetailsSerializer(payments)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, payment, format=None):
        payment_obj = SalePayments.objects.get(pk=payment)
        serializer = CreateUpdatePaymentSerializer(payment_obj, data=request.data)
        if serializer.is_valid():
            invoice = request.data['sales_invoice']
            # check the total for invoice
            if update_invoice_status(invoice=invoice, current=request.data['Amount'],
                                     update=payment) == "error":
                return HttpResponse({"failed: the Invoice can't be over-paid"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            # create record history
            add_record_history(activity_type="update_payment",
                               sale=payment_obj.sales_invoice,
                               add_by=request.user.employee,
                               activity_id=payment,
                               )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, payment):
        obj = SalePayments.objects
        obj.sales_invoice.paid = False
        # add delete record
        delete_payment = deletedActivities.objects.create(
            amount=obj.Amount,
            payment_method=obj.method,
            status=obj.status,
            payment=obj.id,
        )
        # create record history
        add_record_history(activity_type="delete_payment",
                           sale=obj.sales_invoice,
                           add_by=request.user.employee,
                           activity_id=delete_payment.id,
                           )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentCreate(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        r = RolesPermissionsCheck(request, "can_add_paymentForBills")
        r.has_permission()
        serializer = CreateUpdatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            # check the total for invoice
            if update_invoice_status(invoice=request.data['sales_invoice'], current=request.data['Amount']) == "error":
                return HttpResponse({"failed: the Invoice can't be over-paid"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            # create record history
            invoice = SaleInvoice.objects.get(pk=serializer.data['sales_invoice'])
            employee = Employees.objects.get(pk=serializer.data['Collected_by'])
            add_record_history(activity_type="create_payment",
                               sale=invoice,
                               add_by=employee,
                               activity_id=serializer.data['id'],
                               )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceStore(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, invoice):
        products = SaleInvoice_products.objects.filter(sales_invoice=invoice)
        serializer = InvoiceStoreSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# todo send email recordhistory

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_invoice_recordhistory(request, invoice):
    events = RecordHistory.objects.filter(sale=invoice)
    data = []

    for item in events:
        if item.type == 'create_sale' or item.type == 'update_invoice':
            data_obj = SaleInvoice.objects.get(id=item.activity_id)
            customer = data_obj.customer.user
            obj = {
                'type': item.type,
                "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "paid": data_obj.paid,
                "invoice_id": data_obj.id,
                "customer_name": customer.first_name,
                "customer_id": customer.id,
                "total": data_obj.total
            }
            data.append(obj)
        elif item.type == 'sold_product' or item.type == 'update_product_invoice' or item.type == 'delete_product_invoice':
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
            except:
                data_obj = deletedActivities.objects.get(product=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "invoice_id": invoice,
                    "product_id": item.product.id,
                    "product_name": item.product.name,
                    "unit_price": data_obj.amount,
                    "items": data_obj.item_count,
                    "store": data_obj.store_count
                }
            data.append(obj)
        elif item.type == 'create_payment' or item.type == 'update_payment' or item.type == 'delete_payment':
            try:
                data_obj = SalePayments.objects.get(pk=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "payment_id": data_obj.id,
                    "amount": data_obj.Amount,
                    "method": data_obj.method,
                    "status": data_obj.status,
                    "invoice_total": data_obj.sales_invoice.total,
                    "invoice_status": data_obj.sales_invoice.paid,
                }
            except:
                data_obj = deletedActivities.objects.get(payment=item.activity_id)
                invoice_obj = SaleInvoice.objects.get(pk=invoice)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "payment_id": data_obj.id,
                    "amount": data_obj.amount,
                    "method": data_obj.payment_method,
                    "status": data_obj.status,
                    "invoice_total": invoice_obj.total,
                    "invoice_status": invoice_obj.paid,
                }
            data.append(obj)
        final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_customer(request):
    customers = Customers.objects.all().order_by("id")
    data = []
    for item in customers:
        obj = {
            "name": item.user.first_name,
            "id": item.id
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_products(request):
    products = Products.objects.filter(deactivate=False).order_by("id")
    data = []
    for item in products:
        obj = {
            "name": item.name,
            "id": item.id,
            "count": item.product_count(item.id),
            "selling_price": item.selling_price,
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_warehouse(request):
    warehouses = Warehouses.objects.filter(deactivate=False).order_by("id")
    data = []
    for item in warehouses:
        obj = {
            "name": item.name,
            "id": item.id,
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')

# @api_view(['GET'])
# # # @permission_classes(())
# def get_invoice_store(request, invoice):
#     products = SaleInvoice_products.objects.filter(sales_invoice_id=invoice)
#     data = []
#     for item in products:
#         obj = {
#             "product_name": item.product.name,
#             "product_id": item.product.id,
#             "quantity": item.quantity,
#             "count_after": item.count_after,
#         }
#         data.append(obj)
#     final=json.dumps(data)
#     return HttpResponse(final, content_type='application/json; charset=utf-8')
