import json

from django.db.models import ProtectedError
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsEmployee, RolesPermissionsCheck
from .serializers import *
from Sales.models import SaleInvoice


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
        # RolesPermissionsCheck(request, "can_show_suppliers")
        suppliers = Suppliers.objects.all()
        data = []
        for supplier in suppliers:
            obj = {
                "id": supplier.id,
                "business_name": supplier.business_name,
                "name": supplier.user.first_name + " " + supplier.user.last_name,
                "is_active": supplier.user.is_active,
                "country": supplier.user.country,
                "add_by": supplier.add_by.user.first_name + " " + supplier.add_by.user.last_name,
            }
            data.append(obj)
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        # RolesPermissionsCheck(request, "can_add_supplier")
        serializer = SuppliersSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data, user_request=request.user.employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_supplier")
        for item in request.data:
            supplier = Suppliers.objects.get(id=item)
            try:
                supplier.delete()
            except ProtectedError:
                pass
        return Response({"done"}, status=status.HTTP_204_NO_CONTENT)


class GetUpdateDeleteSupplier(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, supplier):
        suppliers = Suppliers.objects.get(id=supplier)
        serializer = getSupplierSerializer(suppliers)
        obj = serializer.data
        try:
            all_invoices = PurchaseInvoice.objects.filter(supplier=supplier)
            invoice_due = PurchaseInvoice.objects.filter(supplier=supplier, paid=False)
            last_invoice = all_invoices.latest("id")
            obj["invoiceDue"] = invoice_due.count()
            obj["allInvoices"] = all_invoices.count()
            obj["lastInvoice"] = last_invoice.id
        except ObjectDoesNotExist:
            pass
        return Response(obj, status=status.HTTP_200_OK)

    def put(self, request, supplier):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_supplier")
        supplier = Suppliers.objects.get(pk=supplier)
        user = supplier.user
        user.email = "  "
        user.save()
        serializer = SuppliersSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=supplier, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, supplier):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_supplier")
        supplier = Suppliers.objects.get(pk=supplier)
        supplier.delete()
        return Response("done", status=status.HTTP_204_NO_CONTENT)


class GetSupplierPurchases(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, supplier):
        # RolesPermissionsCheck(request, "can_show_suppliers")
        purchases = PurchaseInvoice.objects.filter(supplier_id=supplier)
        serializer = SupplierPurchasesSerializer(purchases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetCreateCustomers(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        # RolesPermissionsCheck(request, "can_show_customers")
        customers = Customers.objects.all()
        data = []
        for customer in customers:
            obj = {
                "name": customer.user.first_name + " " + customer.user.last_name,
                "phone": customer.user.phone,
                "id": customer.id,
                "city": customer.user.city,
                "address": customer.user.address,
                "email": customer.user.email
            }
            data.append(obj)
        final = json.dumps(data)
        return HttpResponse(final, content_type='application/json; charset=utf-8')

    def post(self, request):
        # RolesPermissionsCheck(request, "can_add_customer")
        serializer = CreateUpdateCustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_customers")
        for item in request.data:
            obj = Customers.objects.get(id=item)
            try:
                obj.delete()
            except ProtectedError:
                pass
        return Response({"done"}, status=status.HTTP_204_NO_CONTENT)


class GetCustomerDetails(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, customer):
        # RolesPermissionsCheck(request, "can_show_customers")
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
        # RolesPermissionsCheck(request, "can_edit_Or_delete_customers")
        obj = Customers.objects.get(id=customer)
        user = obj.user
        user.email = "  "
        user.save()
        serializer = CreateUpdateCustomerSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, customer):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_customers")
        obj = Customers.objects.get(id=customer)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TODO chango to show active users only and suplier and employee

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
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        # RolesPermissionsCheck(request, "can_show_employees")
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
        # RolesPermissionsCheck(request, "can_add_employee")
        serializer = CreateUpdateEmployeeSerializer(data=request.data.dict())
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data.dict(), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_employee")
        for item in request.data:
            obj = Employees.objects.get(id=item)
            try:
                obj.delete()
            except ProtectedError:
                pass
        return Response({"done"}, status=status.HTTP_204_NO_CONTENT)


class UpdateDeleteEmployees(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, employee):
        # RolesPermissionsCheck(request, "can_show_employees")
        obj = Employees.objects.get(id=employee)
        serializer = CreateUpdateEmployeeSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, employee):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_employee")
        obj = Employees.objects.get(id=employee)
        user = obj.user
        user.email = "  "
        user.save()
        serializer = CreateUpdateEmployeeSerializer(obj, data=request.data.dict())
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data.dict())
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, employee):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_employee")
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
        # RolesPermissionsCheck(request, "can_edit_feesSettings")
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
        # RolesPermissionsCheck(request, "can_edit_feesSettings")
        obj = Tax.objects.get(id=tax)
        serializer = TaxSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tax):
        # RolesPermissionsCheck(request, "can_edit_feesSettings")
        obj = Tax.objects.get(id=tax)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetCreateRoles(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        # RolesPermissionsCheck(request, "can_management_roles")
        obj = RolePermissions.objects.all()
        serializer = RoleSerializer(obj, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # RolesPermissionsCheck(request, "can_management_roles")
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateDeleteRole(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, role):
        # RolesPermissionsCheck(request, "can_management_roles")
        obj = RolePermissions.objects.get(id=role)
        serializer = RoleSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, role):
        # RolesPermissionsCheck(request, "can_management_roles")
        obj = RolePermissions.objects.get(id=role)
        serializer = RoleSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.update(instance=obj, validated_data=request.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, role):
        # RolesPermissionsCheck(request, "can_management_roles")
        obj = RolePermissions.objects.get(id=role)
        try:
            obj.delete()
        except ProtectedError:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateNotesActions(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def post(self, request):
        serializer = NotesActionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteNotesActions(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, note):
        obj = NotesActions.objects.get(id=note)
        serializer = NotesActionsSerializer(obj)
        return Response(serializer.data)

    def put(self, request, note):
        obj = NotesActions.objects.get(id=note)
        serializer = NotesActionsSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, note):
        obj = NotesActions.objects.get(id=note)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetNotesActions(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, type):
        objects = NotesActions.objects.filter(type=type)
        serializer = NotesActionsSerializer(objects, many=True)
        return Response(serializer.data)


class CreateNotes(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = NotesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteNotes(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, note):
        obj = Notes.objects.get(id=note)
        serializer = NotesActionsSerializer(obj)
        return Response(serializer.data)

    def put(self, request, note):
        obj = Notes.objects.get(id=note)
        serializer = NotesSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, note):
        obj = Notes.objects.get(id=note)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetNotes(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, type):
        objects = NotesActions.objects.filter(type=type)
        serializer = NotesSerializer(objects, many=True)
        return Response(serializer.data)
