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
        self.has_permission()

    def checkRole(self):
        if self.type == "can_add_paymentForBills":
            return self.employee.role.can_add_paymentForBills
        elif self.type == "can_add_purchaseBill":
            return self.employee.role.can_add_purchaseBill
        elif self.type == "can_edit_Or_delete_purchaseBill":
            return self.employee.role.can_edit_Or_delete_purchaseBill
        elif self.type == "can_show_purchaseBills":
            return self.employee.role.can_show_purchaseBills
        elif self.type == "can_show_his_purchaseBills":
            return self.employee.role.can_show_his_purchaseBills


class IsEmployee(permissions.BasePermission):
    message = "You are not employee"

    def has_permission(self, request, view):
        employee = Employees.objects.filter(user=request.user)
        if employee.exists():
            return True
        return False
