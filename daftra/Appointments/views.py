import json
from datetime import timedelta, datetime

from django.core.mail import send_mail
from django.db.models import ProtectedError
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Users.models import Customers
from .permissions import IsEmployee, RolesPermissionsCheck
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from Users.models import *


class getCreateAppointments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        # RolesPermissionsCheck(request, "show_appointment")
        objects = Appointments.objects.all()
        serializer = AppointmentsSerializer(objects, many=True)
        for item in serializer.data:
            duration = int(item.get("duration"))
            time = datetime.strptime(item.get("time"), "%H:%M:%S") + timedelta(minutes=duration)
            item["end"] = time.strftime("%H:%M:%S")
            customer = Customers.objects.get(id=item.get("customer"))
            item["customer_name"] = customer.user.first_name + " " + customer.user.last_name
            item["customer_email"] = customer.user.email
            item["customer_phone"] = customer.user.phone
        final = json.dumps(serializer.data)
        return HttpResponse(final, status=200)

    def post(self, request):
        # RolesPermissionsCheck(request, "create_appointment")
        send = request.data.pop("share_with_customer")
        serializer = AppointmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            subject = "Maha beauty(New appointment)"
            message = f"You have new appointment on {serializer.data['date'] + ' ' + serializer.data['time']}  "
            customer_email = Customers.objects.get(id=serializer.data['customer']).user.email
            if send:
                send_mail(subject=subject,
                          message=message,
                          recipient_list=[customer_email, ],
                          from_email='no-reply@maha-beauty.net')
            return HttpResponse(serializer.data, status=200)
        return HttpResponse(serializer.errors, status=400)

    def delete(self, request):
        # RolesPermissionsCheck(request, "can_edit_Or_delete_employee")
        for item in request.data:
            obj = Appointments.objects.get(id=item)
            try:
                obj.delete()
            except ProtectedError:
                pass
        return HttpResponse({"done"}, status=204)


class GetUpdateDeleteAppointments(APIView):
    # permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, appointment):
        # RolesPermissionsCheck(request, "update_appointment")
        obj = Appointments.objects.get(id=appointment)
        serializer = AppointmentsSerializer(obj)
        obj = serializer.data
        customer = Customers.objects.get(id=obj.get("customer"))

        obj["customer_name"] = customer.user.first_name + " " + customer.user.last_name
        try:
            employee = Employees.objects.get(id=obj.get("employee"))
            obj["employee_name"] = employee.user.first_name + " " + employee.user.last_name
        except ObjectDoesNotExist:
            pass
        action = actions.objects.get(id=obj.get("action"))
        obj["action_name"] = action.name
        return HttpResponse(json.dumps(obj), status=200)

    def put(self, request, appointment):
        # RolesPermissionsCheck(request, "update_appointment")
        obj = Appointments.objects.get(id=appointment)
        send = request.data.pop("share_with_customer")
        serializer = AppointmentsSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            subject = "Maha beauty(Update Your appointment)"
            message = f"You have new appointment on {serializer.data['date'] + ' ' + serializer.data['time']}  "
            customer_email = Customers.objects.get(id=serializer.data['customer']).user.email
            if send:
                send_mail(subject=subject,
                          message=message,
                          recipient_list=[customer_email, ],
                          from_email='no-reply@maha-beauty.net')
            return HttpResponse(serializer.data, status=200)
        return HttpResponse(serializer.errors, status=400)

    def delete(self, request, appointment):
        # RolesPermissionsCheck(request, "delete_appointment")
        obj = Appointments.objects.get(id=appointment)
        obj.delete()
        return HttpResponse({"done"}, status=204)


class getCreateAppointmentsActions(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        objects = actions.objects.all()
        serializer = AppointmentActionsSerializer(objects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AppointmentActionsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteAppointmentsActions(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, action):
        obj = actions.objects.get(id=action)
        serializer = AppointmentActionsSerializer(obj)

        return Response(serializer.data)

    def put(self, request, action):
        obj = actions.objects.get(id=action)
        serializer = AppointmentActionsSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, action):
        obj = actions.objects.get(id=action)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateStatus(APIView):
    def put(self, request, id):
        appointment = Appointments.objects.get(id=id)
        appointment.status = request.data.get("status")
        appointment.save()
        return HttpResponse({"done"}, status=200)
