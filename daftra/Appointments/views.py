import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import *
from .serializers import *


class getCreateAppointments(APIView):
    def get(self, request):
        objects = Appointments.objects.all()
        serializer = AppointmentsSerializer(objects, many=True)
        return Response(serializer.data)
