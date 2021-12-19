from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *
from Purchases.models import PurchaseInvoice
import random
import string


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = user.first_name
        token['first_name'] = user.last_name
        token['role'] = user.employee.role.id
        token['id'] = user.employee.id
        return token


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["country", "city", "first_name", "last_name", "phone", "phone", "telephone", "middle_name", "address",
                  "notes", "email", "postal_code"]


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["country", "first_name", "last_name"]


class SuppliersSerializer(serializers.ModelSerializer):
    user = CreateUserSerializer(read_only=True)

    class Meta:
        model = Suppliers
        fields = ["id", "business_name", "Tax_id", "commercial_record", "user"]

    def create(self, validated_data):
        user_data = validated_data.get("user")
        random_num = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
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
            password=random_num,
        )
        user.set_password(user.password)
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
        user.email = user_data['email']
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


class getSupplierSerializer(serializers.ModelSerializer):
    user = CreateUserSerializer(read_only=True)

    class Meta:
        model = Suppliers
        fields = ["id", "business_name", "Tax_id", "commercial_record", "user"]


class SupplierPurchasesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y")

    class Meta:
        model = PurchaseInvoice
        fields = ["Received", "created_at", "id", "total"]


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

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user")
        user = User.objects.get(id=instance.user.id)
        user.first_name = user_data['first_name']
        user.last_name = user_data["last_name"]
        user.phone = user_data['phone']
        user.email = user_data['email']
        user.telephone = user_data['telephone']
        user.middle_name = user_data['middle_name']
        user.address = user_data['address']
        user.city = user_data['city']
        user.country = user_data['country']
        user.notes = user_data['notes']
        user.postal_code = user_data['postal_code']
        instance.currency = validated_data.get("currency")
        user.save()
        instance.save()
        return instance


class CreateUpdateEmployeeSerializer(serializers.ModelSerializer):
    user = CreateUserSerializer()
    photo = serializers.FileField(required=False)

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
        user.email = user_data['email']
        user.telephone = user_data['telephone']
        user.middle_name = user_data['middle_name']
        user.address = user_data['address']
        user.city = user_data['city']
        user.country = user_data['country']
        user.notes = user_data['notes']
        user.postal_code = user_data['postal_code']
        instance.role_id = validated_data.get("role")
        try:
            instance.photo = validated_data.get("photo")
        except KeyError:
            pass
        user.save()
        instance.save()
        return instance


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ["tax_name", "id", "tax_value", "product_included"]


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermissions
        fields = '__all__'
