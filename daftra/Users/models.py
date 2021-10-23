from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        self.email = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


user_type = (
    ('customer', "customer"),
    ('employee', "employee"),
    ('supplier', "supplier")

)


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True,blank=True)
    telephone = models.CharField(max_length=11, null=True,blank=True)
    username = None
    type = models.CharField(max_length=8, choices=user_type, default='customer')
    middle_name = models.CharField(max_length=15, null=True,blank=True)
    address = models.CharField(max_length=50, null=True,blank=True)
    city = models.CharField(max_length=15, null=True,blank=True)
    country = models.CharField(max_length=15, null=True,blank=True)
    notes = models.CharField(max_length=150, null=True,blank=True)
    email = models.EmailField(max_length=25, unique=True,blank=True)
    postal_code = models.SmallIntegerField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return str(self.id)


class Customers(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user', related_name='customer')
    currency = models.CharField(max_length=10)


class RolePermissions(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=10)
    can_add_product = models.BooleanField(default=False)
    can_show_products = models.BooleanField(default=False)
    can_edit_Or_delete_products = models.BooleanField(default=False)
    can_add_saleBill = models.BooleanField(default=False)
    can_show_saleBills = models.BooleanField(default=False)
    can_show_his_saleBills = models.BooleanField(default=False)
    can_edit_Or_delete_saleBill = models.BooleanField(default=False)
    can_add_paymentForBills = models.BooleanField(default=False)
    can_edit_feesSettings = models.BooleanField(default=False)
    can_add_customer = models.BooleanField(default=False)
    can_show_customers = models.BooleanField(default=False)
    can_edit_Or_delete_customers = models.BooleanField(default=False)
    can_add_storePermission = models.BooleanField(default=False)
    can_edit_Or_delete_storePermission = models.BooleanField(default=False)
    can_show_storePermissions = models.BooleanField(default=False)
    can_add_purchaseBill = models.BooleanField(default=False)
    can_edit_Or_delete_purchaseBill = models.BooleanField(default=False)
    can_show_purchaseBills = models.BooleanField(default=False)
    can_show_his_purchaseBills = models.BooleanField(default=False)
    can_add_supplier = models.BooleanField(default=False)
    can_edit_Or_delete_supplier = models.BooleanField(default=False)
    can_show_suppliers = models.BooleanField(default=False)
    can_show_his_suppliers = models.BooleanField(default=False)
    can_add_notes = models.BooleanField(default=False)
    can_add_employee = models.BooleanField(default=False)
    can_edit_Or_delete_employee = models.BooleanField(default=False)
    can_management_roles = models.BooleanField(default=False)


class Employees(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user', related_name='employee')
    role = models.ForeignKey(RolePermissions, on_delete=models.CASCADE, db_column='role')
    active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='employee/%y/%m/%d', blank=True, null=True)


class Suppliers(models.Model):
    id = models.AutoField(primary_key=True)
    trade_name = models.CharField(max_length=25)
    Tax_card = models.BigIntegerField(blank=True, null=True)
    commercial_record = models.SmallIntegerField(blank=True, null=True)
    currency = models.CharField(max_length=10)

