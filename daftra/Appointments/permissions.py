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
        if self.type == "create_appointment":
            return self.employee.role.create_appointment
        elif self.type == "update_appointment":
            return self.employee.role.update_appointment
        elif self.type == "delete_appointment":
            return self.employee.role.delete_appointment
        elif self.type == "show_appointment":
            return self.employee.role.delete_appointment

class IsEmployee(permissions.BasePermission):
    message = "You are not employee"

    def has_permission(self, request, view):
        employee = Employees.objects.filter(user=request.user)
        if employee.exists():
            return True
        return False
