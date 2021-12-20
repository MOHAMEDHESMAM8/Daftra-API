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
        self.has_permission()

    def checkRole(self):
        if self.type == "can_add_saleBill":
            return self.employee.role.can_add_saleBill
        elif self.type == "can_show_saleBills":
            return self.employee.role.can_show_saleBills
        elif self.type == "can_show_his_saleBills":
            return self.employee.role.can_show_his_saleBills
        elif self.type == "can_edit_Or_delete_saleBill":
            return self.employee.role.can_edit_Or_delete_saleBill
        elif self.type == "can_add_paymentForBills":
            return self.employee.role.can_add_paymentForBills


class IsEmployee(permissions.BasePermission):
    message = "You are not employee"

    def has_permission(self, request, view):
        employee = Employees.objects.filter(user=request.user)
        if employee.exists():
            return True
        return False
