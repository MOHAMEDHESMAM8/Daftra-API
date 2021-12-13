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
        user.middle_name = user_data['middle_name']
        user.address = user_data['address']
        user.city = user_data['city']
        user.country = user_data['country']
        user.notes = user_data['notes']
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


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["country", "city", "first_name", "last_name", "phone", "phone", "telephone", "middle_name", "address",
                  "notes", "email", "postal_code"]


class CreateUpdateCustomerSerializer(serializers.ModelSerializer):
    user = CreateUserSerializer()

    class Meta:
        model = Customers
        fields = ['currency', 'user']

    def create(self, validated_data):
        user = validated_data.pop("user")
        user = CreateUserSerializer.create(CreateUserSerializer(), user)
        customer = Customers.objects.create(user=user, currency=validated_data.pop("currency"))
        return customer


class CreateUpdateEmployeeSerializer(serializers.ModelSerializer):
    user = CreateUserSerializer()

    class Meta:
        model = Employees
        fields = ['role', 'photo', 'user']

    def create(self, validated_data):
        user = validated_data.pop("user")
        user = CreateUserSerializer.create(CreateUserSerializer(), user)
        employee = Employees.objects.create(user=user, role_id=validated_data.pop("role"),
                                            photo=validated_data.pop('photo')
                                            )
        return employee

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.get(id=instance.user.id)
        user.first_name = user_data['first_name']
        user.last_name = user_data["last_name"]
        user.phone = user_data['phone']
        user.telephone = user_data['telephone']
        user.middle_name = user_data['middle_name']
        user.address = user_data['address']
        user.city = user_data['city']
        user.country = user_data['country']
        user.notes = user_data['notes']
        user.postal_code = user_data['postal_code']
        instance.role_id = validated_data.get("role")
        instance.photo = validated_data.get("photo")
        user.save()
        instance.save()
        return instance


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ["tax_name", "id", "tax_value", "product_included"]

