from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from Purchases.models import PurchaseInvoice


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['role'] = user.employee.role.role
        return token


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["country", "first_name", "last_name"]


class SuppliersSerializer(serializers.ModelSerializer):
    user = UsersSerializer(read_only=True)

    class Meta:
        model = Suppliers
        fields = ["id", "business_name", "Tax_id", "commercial_record", "user"]

    def create(self, validated_data):
        user_data = validated_data.get("user")
        user = User.objects.create(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            telephone=user_data['telephone'],
            type=user_data['type'],
            middle_name=user_data['middle_name'],
            address=user_data['address'],
            city=user_data['city'],
            country=user_data['country'],
            notes=user_data['notes'],
            email=user_data['email'],
            postal_code=user_data['postal_code'],
            password=user_data['password'],
        )
        user.set_password(user_data['password'])
        user.save()
        supplier = Suppliers.objects.create(user=user,
                                            business_name=validated_data.get("business_name"),
                                            Tax_id=validated_data.get("Tax_id"),
                                            commercial_record=validated_data.get("commercial_record"),

                                            )
        return supplier

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.get(id=instance.user.id)

        user.first_name = user_data['first_name']
        user.last_name = user_data["last_name"]
        user.phone = user_data['phone']
        user.telephone = user_data['telephone']
        user.type = user_data['type']
        user.middle_name = user_data['middle_name']
        user.address = user_data['address']
        user.city = user_data['city']
        user.country = user_data['country']
        user.notes = user_data['notes']
        # user.email = user_data['email']
        user.postal_code = user_data['postal_code']
        instance.business_name = validated_data.get("business_name")
        instance.Tax_id = validated_data.get("Tax_id")
        instance.commercial_record = validated_data.get("commercial_record")
        instance.save()
        user.save()
        return instance


class SupplierPurchasesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y")

    class Meta:
        model = PurchaseInvoice
        fields = ["Received", "created_at", "id", "total"]

