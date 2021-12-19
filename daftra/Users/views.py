import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsEmployee, RolesPermissionsCheck
from Sales.views import dictfetchall
from .serializers import *
from Sales.models import SaleInvoice
from django.db import connection


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    token_obtain_pair = TokenObtainPairView.as_view()


class BlacklistTokenUpdateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetCreateSupplier(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        r = RolesPermissionsCheck(request, "can_show_suppliers")
        r.has_permission()
        suppliers = Suppliers.objects.all()
        serializer = SuppliersSerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        r = RolesPermissionsCheck(request, "can_add_supplier")
        r.has_permission()
        serializer = SuppliersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteSupplier(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, supplier):
        suppliers = Suppliers.objects.get(id=supplier)
        serializer = getSupplierSerializer(suppliers)
        obj = serializer.data
        all_invoices = PurchaseInvoice.objects.filter(supplier=supplier)
        invoice_due = PurchaseInvoice.objects.filter(supplier=supplier, paid=False)
        last_invoice = all_invoices.latest("id")
        obj["invoiceDue"] = invoice_due.count()
        obj["allInvoices"] = all_invoices.count()
        obj["lastInvoice"] = last_invoice.id
        return Response(obj, status=status.HTTP_200_OK)

    def put(self, request, supplier):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_supplier")
        r.has_permission()
        supplier = Suppliers.objects.get(pk=supplier)
        serializer = SuppliersSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=supplier, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, supplier):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_supplier")
        r.has_permission()
        supplier = Suppliers.objects.get(pk=supplier)
        supplier.delete()
        return Response("done", status=status.HTTP_204_NO_CONTENT)


class GetSupplierPurchases(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, supplier):
        r = RolesPermissionsCheck(request, "can_show_suppliers")
        r.has_permission()
        purchases = PurchaseInvoice.objects.filter(supplier_id=supplier)
        serializer = SupplierPurchasesSerializer(purchases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCreateCustomers(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        r = RolesPermissionsCheck(request, "can_show_customers")
        r.has_permission()
        customers = Customers.objects.all()
        data = []
        for customer in customers:
            obj = {
                "name": customer.user.first_name + " " + customer.user.last_name,
                "phone": customer.user.phone,
                "id": customer.id,
                "city": customer.user.city,
                "address": customer.user.address
            }
            data.append(obj)
        final = json.dumps(data)
        return HttpResponse(final, content_type='application/json; charset=utf-8')

    def post(self, request):
        r = RolesPermissionsCheck(request, "can_add_customer")
        r.has_permission()
        serializer = CreateUpdateCustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetCustomerDetails(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, customer):
        r = RolesPermissionsCheck(request, "can_show_customers")
        r.has_permission()
        customer_obj = Customers.objects.get(id=customer)
        serializer = CreateUpdateCustomerSerializer(customer_obj)
        obj = serializer.data
        try:
            allInvoices = SaleInvoice.objects.filter(customer=customer)
            invoiceDue = SaleInvoice.objects.filter(customer=customer, paid=False)
            lastInvoice = allInvoices.latest("id")
            big = 0
            total = 0
            paymentTotal = 0
            for item in allInvoices:
                total += item.total
                for i in item.SalePayments.all():
                    paymentTotal += i.Amount
                try:
                    object = item.SalePayments.all().latest("id")
                    if object.id > big:
                        big += object.id
                except ObjectDoesNotExist:
                    pass
            obj["Invoice Number"] = allInvoices.count()
            obj["invoice Due Number"] = invoiceDue.count()
            obj["Last Invoice"] = lastInvoice.id
            obj["Last Payment"] = big
            obj["total"] = total
            obj["total Payments"] = paymentTotal
            obj["due amount"] = total - paymentTotal
        except ObjectDoesNotExist:
            pass
        return Response(obj, status=status.HTTP_200_OK)

    def put(self, request, customer):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_customers")
        r.has_permission()
        obj = Customers.objects.get(id=customer)
        serializer = CreateUpdateCustomerSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_customers")
        r.has_permission()
        obj = Customers.objects.get(id=customer)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_invoice_customer(request, customer):
    invoices = SaleInvoice.objects.filter(customer=customer)
    data = []
    for item in invoices:
        record = RecordHistory.objects.filter(sale=item.id).latest("id")
        obj = {
            "id": item.id,
            "created_at": item.created_at.strftime("%m/%d/%Y"),
            "activity_date": record.created_at.strftime("%m/%d/%Y"),
            "last_activity": record.type,
            "total": item.total,
            "paid": item.paid,
        }
        data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEmployee])
def get_all_Payment_customer(request, customer):
    invoices = SaleInvoice.objects.filter(customer=customer)
    data = []
    for item in invoices:
        for payment in item.SalePayments.all():
            obj = {
                "id": payment.id,
                "created_at": payment.Date.strftime("%m/%d/%Y"),
                "method": payment.method,
                "Amount": payment.Amount,
                "invoice_id": item.id,
                "Customer": payment.Collected_by.user.first_name + " " + payment.Collected_by.user.last_name,
                "status": payment.status,
            }
            data.append(obj)
    final = json.dumps(data)
    return HttpResponse(final, content_type='application/json; charset=utf-8')


class GetCreateEmployees(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        r = RolesPermissionsCheck(request, "can_show_employees")
        r.has_permission()
        employees = Employees.objects.all()
        data = []
        for employee in employees:
            try:
                las_login = employee.user.last_login.strftime("%m/%d/%Y %H:%M:%S")
            except AttributeError:
                las_login = " "
            obj = {
                "name": employee.user.first_name + " " + employee.user.last_name,
                "phone": employee.user.email,
                "id": employee.id,
                "role": employee.role.role,
                "active": employee.user.is_active,
                "last_login": las_login
            }
            data.append(obj)
        final = json.dumps(data)
        return HttpResponse(final, content_type='application/json; charset=utf-8')

    def post(self, request):
        r = RolesPermissionsCheck(request, "can_add_employee")
        r.has_permission()
        serializer = CreateUpdateEmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteEmployees(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, employee):
        r = RolesPermissionsCheck(request, "can_show_employees")
        r.has_permission()
        obj = Employees.objects.get(id=employee)
        serializer = CreateUpdateEmployeeSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, employee):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_employee")
        r.has_permission()
        obj = Employees.objects.get(id=employee)
        serializer = CreateUpdateEmployeeSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee):
        r = RolesPermissionsCheck(request, "can_edit_Or_delete_employee")
        r.has_permission()
        obj = Employees.objects.get(id=employee)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetCreateTaxs(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        obj = Tax.objects.all()
        serializer = TaxSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        r = RolesPermissionsCheck(request, "can_edit_feesSettings")
        r.has_permission()
        serializer = TaxSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteTax(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, tax):
        obj = Tax.objects.get(id=tax)
        serializer = TaxSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tax):
        r = RolesPermissionsCheck(request, "can_edit_feesSettings")
        r.has_permission()
        obj = Tax.objects.get(id=tax)
        serializer = TaxSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tax):
        r = RolesPermissionsCheck(request, "can_edit_feesSettings")
        r.has_permission()
        obj = Tax.objects.get(id=tax)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetCreateRoles(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        r = RolesPermissionsCheck(request, "can_management_roles")
        r.has_permission()
        obj = RolePermissions.objects.all()
        serializer = RoleSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        r = RolesPermissionsCheck(request, "can_management_roles")
        r.has_permission()
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteRole(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, role):
        r = RolesPermissionsCheck(request, "can_management_roles")
        r.has_permission()
        obj = RolePermissions.objects.get(id=role)
        serializer = RoleSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, role):
        r = RolesPermissionsCheck(request, "can_management_roles")
        r.has_permission()
        obj = RolePermissions.objects.get(id=role)
        serializer = RoleSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, role):
        r = RolesPermissionsCheck(request, "can_management_roles")
        r.has_permission()
        obj = RolePermissions.objects.get(id=role)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
