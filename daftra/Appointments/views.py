
from datetime import timedelta,datetime

from django.core.mail import send_mail
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Users.models import Customers
from .permissions import IsEmployee, RolesPermissionsCheck
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *


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
        return Response(serializer.data)

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
                          from_email='hesmammohammed@gmail.com')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteAppointments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, appointment):
        # RolesPermissionsCheck(request, "update_appointment")
        obj = Appointments.objects.get(id=appointment)
        serializer = AppointmentsSerializer(obj)
        return Response(serializer.data)

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
                          from_email='hesmammohammed@gmail.com')
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, appointment):
        # RolesPermissionsCheck(request, "delete_appointment")
        obj = Appointments.objects.get(id=appointment)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
