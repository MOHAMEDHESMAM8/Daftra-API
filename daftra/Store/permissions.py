from rest_framework import permissions
from rest_framework import serializers

from Users.models import Employees


class RolesPermissionsCheck():
    message = f"you can't access this page"
    type = ""
    request = ''

    def __init__(self, request, type):
        self.type = type
        self.request = request
        self.has_permission()

    def has_permission(self, ):
        employee = Employees.objects.get(user=self.request.user)
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
        if self.type == "can_add_product":
            return self.employee.role.can_add_product
        elif self.type == "can_show_products":
            return self.employee.role.can_show_products
        elif self.type == "can_edit_Or_delete_products":
            return self.employee.role.can_edit_Or_delete_products
        elif self.type == "can_edit_Or_delete_customers":
            return self.employee.role.can_edit_Or_delete_customers
        elif self.type == "can_add_storePermission":
            return self.employee.role.can_add_storePermission
        elif self.type == "can_edit_Or_delete_storePermission":
            return self.employee.role.can_edit_Or_delete_storePermission
        elif self.type == "can_show_storePermissions":
            return self.employee.role.can_show_storePermissions


class IsEmployee(permissions.BasePermission):
    message = "You are not employee"

    def has_permission(self, request, view):
        employee = Employees.objects.filter(user=request.user)
        if employee.exists():
            return True
        return False
