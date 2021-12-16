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
from Users.models import RecordHistory
from .permissions import IsEmployee, RolesPermissionsCheck


# update Invoice paid status
def update_invoice_status(invoice, current=0, update=0):
    obj = PurchaseInvoice.objects.get(pk=invoice)
    payments = obj.PurchasePayments.all()
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
        if request.user.employee.role.can_show_purchaseBills:
            cursor.execute("""SELECT
           invoice.id,
           DATE_FORMAT(invoice.created_at, "%d-%m-%Y %H:%m") as created_at_invoice,
           invoice.total,
           invoice.paid,
           invoice.supplier as supplier_id,
           user.first_name as supplier_name
           FROM
               purchases_purchaseinvoice AS invoice
           INNER JOIN users_suppliers AS supplier
           ON
               invoice.supplier = supplier.id
           INNER JOIN users_user AS user
           ON user.id = supplier.user
           """)
        elif request.user.employee.role.can_show_his_purchaseBills:
            n = request.user.employee.id
            query = f"""SELECT
               invoice.id,
               DATE_FORMAT(invoice.created_at, "%d-%m-%Y %H:%m") as created_at_invoice,
               invoice.total,
               invoice.paid,
               invoice.supplier as supplier_id,
               user.first_name as supplier_name
               FROM
                   purchases_purchaseinvoice AS invoice
               INNER JOIN users_suppliers AS supplier
               ON
                   invoice.supplier = supplier.id
               INNER JOIN users_user AS user
               ON user.id = supplier.user
                where invoice.add_by = {n} """
            cursor.execute(query)
        else:
            r = RolesPermissionsCheck(request, "can_show_purchaseBills")
            r.has_permission()

        json_format = json.dumps(dictfetchall(cursor))
        data = json.loads(json_format)
        for item in data:
            invoice = item.get("id")
            record = RecordHistory.objects.filter(purchase=invoice).latest("id")
            item["last_activity"] = record.type
            item['activity_created_at'] = record.created_at.strftime("%m/%d/%Y, %H:%M:%S")
        final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


# todo  check from front upload photo is working
class createPurchaseInvoice(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        invoices = PurchaseInvoice.objects.all()
        serializer = PurchaseInvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        r = RolesPermissionsCheck(request, "can_add_purchaseBill")
        r.has_permission()
        serializer = PurchaseInvoiceSerializer(data=request.data.dict())
        if serializer.is_valid():
            serializer.create(validated_data=request.data.dict(), user=request.user.employee)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# todo  check from front upload photo is working
class updatePurchaseInvoice(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]


    def get(self, request, invoice):
        invoice = PurchaseInvoice.objects.get(pk=invoice)
        serializer = PurchaseInvoiceSerializer(invoice)
        return Response(serializer.data)

    def put(self, request, invoice, format=None):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_purchaseBill")
        r.has_permission()
        invoice = PurchaseInvoice.objects.get(pk=invoice)
        serializer = PurchaseInvoiceSerializer(invoice, request.data.dict())
        if serializer.is_valid():
            serializer.update(instance=invoice, validated_data=request.data.dict())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShowPayments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, invoice):
        payments = PurchaseInvoice.objects.get(pk=invoice)
        serializer = paymentsInvoiceSerializer(payments)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PaymentDetails(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, payment):
        payments = PurchasePayments.objects.get(pk=payment)
        serializer = paymentDetailsSerializer(payments)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, payment, format=None):
        payment_obj = PurchasePayments.objects.get(pk=payment)
        serializer = CreateUpdatePaymentSerializer(payment_obj, data=request.data)
        if serializer.is_valid():
            data = json.loads(request.data.dict())
            invoice = data['purchase_invoice']
            # check the total for invoice
            if update_invoice_status(invoice=invoice, current=data['Amount'],
                                     update=payment) == "error":
                return HttpResponse({"failed: the Invoice can't be over-paid"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            # create record history
            add_record_history(activity_type="update_payment",
                               purchase=payment_obj.purchase_invoice,
                               add_by=request.user.employee,
                               activity_id=payment,
                               )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, payment):
        obj = PurchasePayments.objects
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
                           purchase=obj.purchase_invoice,
                           add_by=request.user.employee,
                           activity_id=delete_payment.id,
                           )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PaymentCreate(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        payments = PurchasePayments.objects.all()
        serializer = paymentsSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        r = RolesPermissionsCheck(request, "can_add_paymentForBills")
        r.has_permission()
        serializer = CreateUpdatePaymentSerializer(data=request.data)
        if serializer.is_valid():
            data = json.loads(request.data.dict())

            # check the total for invoice
            if update_invoice_status(invoice=data['sales_invoice'], current=data['Amount']) == "error":
                return HttpResponse({"failed: the Invoice can't be over-paid"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            # create record history
            invoice = PurchasePayments.objects.get(pk=serializer.data['sales_invoice'])
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
        products = PurchaseInvoice_products.objects.filter(sales_invoice=invoice)
        serializer = InvoiceStoreSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# todo send email recordhistory
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_invoice_recordhistory(request, invoice):
    events = RecordHistory.objects.filter(purchase=invoice)
    data = []

    for item in events:
        if item.type == 'create_purchase' or item.type == 'update_invoice':
            data_obj = PurchaseInvoice.objects.get(id=item.activity_id)
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
        elif item.type == 'receive_product' or item.type == 'update_product_invoice' or item.type == 'delete_product_invoice':
            try:
                data_obj = PurchaseInvoice_products.objects.get(pk=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "invoice_id": data_obj.purchase_invoice.id,
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
                data_obj = PurchasePayments.objects.get(pk=item.activity_id)
                obj = {
                    'type': item.type,
                    "made_by": item.add_by.user.first_name + " " + item.add_by.user.last_name,
                    "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                    "payment_id": data_obj.id,
                    "amount": data_obj.Amount,
                    "method": data_obj.method,
                    "status": data_obj.status,
                    "invoice_total": data_obj.purchase_invoice.total,
                    "invoice_status": data_obj.purchase_invoice.paid,
                }
            except ObjectDoesNotExist:
                data_obj = deletedActivities.objects.get(payment=item.activity_id)
                invoice_obj = PurchaseInvoice.objects.get(pk=invoice)
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
def get_all_supplier(request):
    customers = Suppliers.objects.all().order_by("id")
    data = []
    for item in customers:
        obj = {
            "name": item.user.first_name,
            "id": item.id
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')

