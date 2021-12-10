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
payment_status = (
    ('incomplete', "incomplete"),
    ('complete', "complete"),
    ('pending', "pending"),
    ('failed', "failed"),

)
tax_types = (
    ('inclusive', "inclusive"),
    ('exclusive', "exclusive"),

)
notes_types = (
    ('customer', "customer"),
    ('employee', "employee"),

)
RecordHistory_types = (
    ('update_Store', "update_Store"),
    ('update_invoice', "update_invoice"),
    ('sold_product', "sold_product"),
    ('create_payment', "create_payment"),
    ('update_payment', "update_payment"),
    ('delete_payment', "delete_payment"),
    ('add_addPermission', "add_addPermission"),
    ('add_outPermission', "add_outPermission"),
    ('update_outPermission', "update_outPermission"),
    ('update_addPermission', "update_addPermission"),
    ('delete_addPermission', "delete_addPermission"),
    ('delete_outPermission', "delete_outPermission"),
    ('update_product_addPermission', "update_product_addPermission"),
    ('update_product_outPermission', "update_product_outPermission"),
    ('add_product_addPermission', "add_product_addPermission"),
    ('add_product_outPermission', "add_product_outPermission"),
    ('delete_product_outPermission', "delete_product_outPermission"),
    ('delete_product_addPermission', "delete_product_addPermission"),
    ('receive_product', "receive_product"),
    ('create_purchase', "create_purchase"),
    ('create_sale', "create_sale"),
    ('send_email', "send_email"),
    ('create_appointment', "create_appointment"),
    ('update_appointment', "update_appointment"),
    ('delete_appointment', "delete_appointment"),
    ('move_product', "move_product"),
    ('update_product_invoice', "update_product_invoice"),
    ('delete_product_invoice', "delete_product_invoice"),
    ('update_product', "update_product"),

)
delete_type = (
    ('sales', "sales"),
    ('purchases', "purchases"),

)
payment_methods = (
    ('cash', "cash"),
    ('cheque', "cheque"),
    ('bank transfer', "bank transfer"),
    ('paytabs', "paytabs"),

)


class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=11, null=True, blank=True)
    telephone = models.CharField(max_length=11, null=True, blank=True)
    username = None
    type = models.CharField(max_length=8, choices=user_type, default='customer')
    middle_name = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=15, null=True, blank=True)
    notes = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(max_length=25, unique=True, blank=True)
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
    photo = models.ImageField(upload_to='employee/%y/%m', blank=True, null=True)


class Suppliers(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user', related_name='supplier')
    business_name = models.CharField(max_length=25)
    Tax_id = models.CharField(max_length=30, blank=True, null=True)
    commercial_record = models.CharField(max_length=30, blank=True, null=True)


class Tax(models.Model):
    id = models.AutoField(primary_key=True)
    tax_name = models.CharField(max_length=30)
    tax_value = models.PositiveSmallIntegerField()
    product_included = models.CharField(max_length=10, choices=tax_types)


class emails(models.Model):
    id = models.AutoField(primary_key=True)
    subject = models.CharField(max_length=30)
    send_form = models.CharField(max_length=50)
    send_to = models.CharField(max_length=50)
    invoice = models.ForeignKey('Sales.SaleInvoice', on_delete=models.CASCADE, db_column='invoice')
    message = models.TextField()
    attachment = models.FileField(upload_to='Files/%y/%m')
    created_at = models.DateTimeField(auto_now_add=True)


class RecordHistory(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=40, choices=RecordHistory_types)
    product = models.ForeignKey("Store.Products", db_column='product', on_delete=models.CASCADE, null=True,
                                blank=True)
    outPermissions = models.ForeignKey("Store.OutPermissions", db_column='outPermissions', on_delete=models.CASCADE, null=True,
                                       blank=True)
    addPermissions = models.ForeignKey("Store.AddPermissions", db_column='addPermissions', on_delete=models.CASCADE, null=True,
                                       blank=True)
    customer = models.ForeignKey(Customers, db_column='customer',
                                 on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employees, db_column='employee', on_delete=models.CASCADE, null=True, blank=True,
                                 related_name="employee")
    activity_id = models.PositiveSmallIntegerField()
    purchase = models.ForeignKey("Purchases.PurchaseInvoice", db_column='purchase', on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)
    sale = models.ForeignKey("Sales.SaleInvoice", db_column='sale', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    add_by = models.ForeignKey(Employees, db_column='add_by', on_delete=models.CASCADE, null=True, blank=True)


class deletedActivities(models.Model):
    id = models.AutoField(primary_key=True)
    payment = models.PositiveSmallIntegerField(null=True, blank=True, )
    product = models.PositiveSmallIntegerField(null=True, blank=True, )
    amount = models.PositiveIntegerField(null=True, blank=True, )
    payment_method = models.CharField(choices=payment_methods, max_length=15, null=True, blank=True, )
    status = models.CharField(choices=payment_status, max_length=20, null=True, blank=True, )
    item_count = models.PositiveSmallIntegerField(null=True, blank=True, )
    store_count = models.PositiveSmallIntegerField(null=True, blank=True, )


class Notes(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    notes = models.TextField()
    type = models.CharField(max_length=20, choices=notes_types)
    person_id = models.IntegerField()
    # Todo اجراء تنفيذ CRUD
    # Todo حدث الحالة الى CRUD



class NotesAttachment(models.Model):
    id = models.AutoField(primary_key=True)
    attachment = models.FileField(upload_to='Notes/%y/%m')
    note = models.ForeignKey(Notes, db_column='note', on_delete=models.CASCADE)

