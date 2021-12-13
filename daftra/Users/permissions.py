from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response

from Users.models import Employees


class RolesPermissionsCheck():
    message = f"you can't access this page"
    type = ""
    request = ''

    def __init__(self, request, type):
        self.type = type
        self.request = request

    def has_permission(self, ):
        employee = Employees.objects.get(user=self.request.user.id)
        factory = Factory(self.type, employee)
        if factory.checkRole():
            return True
        raise serializers.ValidationError(self.message, 'permission_denied')


class Factory:
    type = 0
    employee = 0

    def __init__(self, type, employee):
        self.type = type
        self.employee = employee

    def checkRole(self):
        if self.type == "can_edit_feesSettings":
            return self.employee.role.can_edit_feesSettings
        elif self.type == "can_add_customer":
            return self.employee.role.can_add_customer
        elif self.type == "can_show_customers":
            return self.employee.role.can_show_customers
        elif self.type == "can_edit_Or_delete_customers":
            return self.employee.role.can_edit_Or_delete_customers
        elif self.type == "can_add_supplier":
            return self.employee.role.can_add_supplier
        elif self.type == "can_edit_Or_delete_supplier":
            return self.employee.role.can_edit_Or_delete_supplier
        elif self.type == "can_show_suppliers":
            return self.employee.role.can_show_suppliers
        elif self.type == "can_add_notes":
            return self.employee.role.can_add_notes
        elif self.type == "can_add_employee":
            return self.employee.role.can_add_employee
        elif self.type == "can_edit_Or_delete_employee":
            return self.employee.role.can_edit_Or_delete_employee
        elif self.type == "can_management_roles":
            return self.employee.role.can_management_roles
        elif self.type == "can_show_employees":
            return self.employee.role.can_management_roles


class IsEmployee(permissions.BasePermission):
    message = "You are not employee"

    def has_permission(self, request, view):
        employee = Employees.objects.filter(user=request.user)
        if employee.exists():
            return True
        return False
