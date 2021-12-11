from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from Users.models import Employees


class RolesPermissionsCheck():
    message = ""
    type = ""
    request = ''

    def __init__(self, request, type):
        self.type = type
        self.request = request

    def has_permission(self, ):
        employee = Employees.objects.filter(user=1)
        if employee.exists():
            factory = Factory(self.type, employee[0])
            if factory.checkRole():
                return True
            else:
                self.message = f"you can't access this page"
        else:
            self.message = "You are not employee"
        raise serializers.ValidationError(self.message, 'permission_denied')


class Factory:
    type = 0
    employee = 0

    def __init__(self, type, employee):
        self.type = type
        self.employee = employee

    def checkRole(self):
        if self.type == "can_add_product":
            return self.employee.role.can_add_product
        elif self.type == "can_show_products":
            return self.employee.role.can_show_products
        elif self.type == "can_edit_Or_delete_products":
            return self.employee.role.can_edit_Or_delete_products
        elif self.type == "can_add_saleBill":
            return self.employee.role.can_add_saleBill
        elif self.type == "can_show_saleBills":
            return self.employee.role.can_show_saleBills
        elif self.type == "can_show_his_saleBills":
            return self.employee.role.can_show_his_saleBills
        elif self.type == "can_edit_Or_delete_saleBill":
            return self.employee.role.can_edit_Or_delete_saleBill
        elif self.type == "can_add_paymentForBills":
            return self.employee.role.can_add_paymentForBills
        elif self.type == "can_edit_feesSettings":
            return self.employee.role.can_edit_feesSettings
        elif self.type == "can_add_customer":
            return self.employee.role.can_add_customer
        elif self.type == "can_show_customers":
            return self.employee.role.can_show_customers
        elif self.type == "can_edit_Or_delete_customers":
            return self.employee.role.can_edit_Or_delete_customers
        elif self.type == "can_add_storePermission":
            return self.employee.role.can_add_storePermission
        elif self.type == "can_edit_Or_delete_storePermission":
            return self.employee.role.can_edit_Or_delete_storePermission
        elif self.type == "can_show_storePermissions":
            return self.employee.role.can_show_storePermissions
        elif self.type == "can_add_purchaseBill":
            return self.employee.role.can_add_purchaseBill
        elif self.type == "can_edit_Or_delete_purchaseBill":
            return self.employee.role.can_edit_Or_delete_purchaseBill
        elif self.type == "can_show_purchaseBills":
            return self.employee.role.can_show_purchaseBills
        elif self.type == "can_show_his_purchaseBills":
            return self.employee.role.can_show_his_purchaseBills
        elif self.type == "can_add_supplier":
            return self.employee.role.can_add_supplier
        elif self.type == "can_edit_Or_delete_supplier":
            return self.employee.role.can_edit_Or_delete_supplier
        elif self.type == "can_show_suppliers":
            return self.employee.role.can_show_suppliers
        elif self.type == "can_show_his_suppliers":
            return self.employee.role.can_show_his_suppliers
        elif self.type == "can_add_notes":
            return self.employee.role.can_add_notes
        elif self.type == "can_add_employee":
            return self.employee.role.can_add_employee
        elif self.type == "can_edit_Or_delete_employee":
            return self.employee.role.can_edit_Or_delete_employee
        elif self.type == "can_management_roles":
            return self.employee.role.can_management_roles
