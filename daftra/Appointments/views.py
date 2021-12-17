import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsEmployee, RolesPermissionsCheck
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *


class getCreateAppointments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request):
        r = RolesPermissionsCheck(request, "show_appointment")
        r.has_permission()

        objects = Appointments.objects.all()
        serializer = AppointmentsSerializer(objects, many=True)
        return Response(serializer.data)

    def post(self, request):
        r = RolesPermissionsCheck(request, "create_appointment")
        r.has_permission()
        serializer = AppointmentsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteAppointments(APIView):
    permission_classes = [IsAuthenticated, IsEmployee]

    def get(self, request, appointment):
        r = RolesPermissionsCheck(request, "update_appointment")
        r.has_permission()
        obj = Appointments.objects.get(id=appointment)
        serializer = AppointmentsSerializer(obj)
        return Response(serializer.data)

    def put(self, request, appointment):
        r = RolesPermissionsCheck(request, "update_appointment")
        r.has_permission()
        obj = Appointments.objects.get(id=appointment)
        serializer = AppointmentsSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, appointment):
        r = RolesPermissionsCheck(request, "delete_appointment")
        r.has_permission()
        obj = Appointments.objects.get(id=appointment)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
