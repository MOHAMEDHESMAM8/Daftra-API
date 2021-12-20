from django.db.models import ProtectedError
from django.http import HttpResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
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


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_invoice(request):
    # if request.user.employee.role.can_show_saleBills:
    invoices = SaleInvoice.objects.all()
    data = []
    for invoice in invoices:
        obj = {
            "id": invoice.id,
            "created_at_invoice": invoice.created_at.strftime("%d-%m-%Y %H:%m"),
            "total": invoice.total,
            "paid": invoice.paid,
            "customer": invoice.customer.id,
            "customer_name": invoice.customer.user.first_name + " " + invoice.customer.user.last_name,
        }
        data.append(obj)

    # elif request.user.employee.role.can_show_his_saleBills:
    #     n = request.user.employee.id
    #     invoices = SaleInvoice.objects.all(sold_by = n)
    #     data = []
    #     for invoice in invoices:
    #         obj = {
    #             "id": invoice.id,
    #             "created_at": invoice.created_at.strftime("%d-%m-%Y %H:%m"),
    #             "total": invoice.total,
    #             "paid": invoice.paid,
    #             "customer": invoice.customer,
    #             "customer_name": invoice.customer.user.first_name + " " + invoice.customer.user.last_name,
    #         }
    #         data.append(obj)
    # else:
    #     # RolesPermissionsCheck(request, "can_show_saleBills")

    for item in data:
        invoice = item.get("id")
        record = RecordHistory.objects.filter(sale=invoice).latest("id")
        item["last_activaty"] = record.type
        item['created_at'] = record.created_at.strftime("%m/%d/%Y, %H:%M:%S")
    final = json.dumps(data)
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
        # RolesPermissionsCheck(request, "can_add_saleBill")
        serializer = SaleInvoiceSerializer(data=request.data.dict())
        if serializer.is_valid():
            invoice = serializer.create(validated_data=request.data.dict(), user=request.user.employee)
            obj = serializer.data
            obj["id"] = invoice.id
            return Response(obj, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_saleBill")
        for item in request.data:
            obj = SaleInvoice.objects.get(id=item)
            try:
                obj.delete()
            except ProtectedError:
                pass
        return Response({"done"}, status=status.HTTP_204_NO_CONTENT)


# todo  check from front upload photo is working
class updateSaleInvoice(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser, FileUploadParser]

    def get(self, request, id):
        invoice = SaleInvoice.objects.get(pk=id)
        serializer = SaleInvoiceSerializer(invoice)
        obj = serializer.data
        obj["customer_name"] = invoice.customer.user.first_name + " " + invoice.customer.user.last_name
        obj["address"] = invoice.customer.user.address
        obj["city"] = invoice.customer.user.city
        obj["country"] = invoice.customer.user.country
        obj["phone"] = invoice.customer.user.phone
        obj["warehouse_name"] = invoice.warehouse.name
        if invoice.sales_officer is not None:
            obj[
                "sales_officer_name"] = invoice.sales_officer.user.first_name + " " + invoice.sales_officer.user.last_name

        for item in obj.get("SaleInvoice_products"):
            print(item)
            product = Products.objects.get(id=item.get("product"))
            item['product_name'] = product.name
            try:
                tax1 = Tax.objects.get(id=item.get("tax1"))
                item['tax1_name'] = tax1.tax_name
            except ObjectDoesNotExist:
                pass
            try:
                tax2 = Tax.objects.get(id=item.get("tax2"))
                item['tax2_name'] = tax2.tax_name
            except ObjectDoesNotExist:
                pass
        amount_of_paid = 0
        for item in invoice.SalePayments.all():
            amount_of_paid += item.Amount
        obj["amount_of_paid"] = amount_of_paid

        return Response(obj)

    def put(self, request, id, format=None):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_saleBill")
        invoice = SaleInvoice.objects.get(pk=id)
        serializer = UpdateSaleInvoiceSerializer(invoice, request.data.dict())
        if serializer.is_valid():
            serializer.update(instance=invoice, validated_data=request.data.dict())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_saleBill")
        obj = SaleInvoice.objects.get(id=id)
        obj.delete()
        return Response({"done"}, status=status.HTTP_204_NO_CONTENT)


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
        serializer = CreateUpdatePaymentSerializer(payment_obj, data=request.data.dict())
        if serializer.is_valid():
            data = json.loads(request.data.dict())
            invoice = data['sales_invoice']
            # check the total for invoice
            if update_invoice_status(invoice=invoice, current=data['Amount'],
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

    def get(self, request):
        payments = SalePayments.objects.all()
        serializer = paymentsSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        # RolesPermissionsCheck(request, "can_add_paymentForBills")
        serializer = CreateUpdatePaymentSerializer(data=request.data.dict())
        if serializer.is_valid():
            data = json.loads(request.data.dict())
            # check the total for invoice
            if update_invoice_status(invoice=data['sales_invoice'], current=data['Amount']) == "error":
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
                    "invoice_id": data_obj.sales_invoice.id,
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
                    "invoice_id": invoice_obj.id,
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
        if not item.user.is_active:
            continue
        obj = {
            "name": item.user.first_name + " " + item.user.last_name,
            "id": item.id
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_employee(request):
    employee = Employees.objects.all().order_by("id")
    data = []
    for item in employee:
        if not item.user.is_active:
            continue
        obj = {
            "name": item.user.first_name + " " + item.user.last_name,
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
            "purchasing_price": item.purchasing_price,
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
