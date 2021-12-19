from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *


class AppointmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointments
        fields = ["id", "date", "duration", "time", "action", "notes", "status", "add_by", "customer", "employee"]


class AppointmentActionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = actions
        fields = '__all__'
