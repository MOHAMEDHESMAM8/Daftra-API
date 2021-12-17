from django.db import models

# Create your models here.
from django.db import models

from Users.models import get_deleted_employee

discount_types = (
    ('percentage', "percentage"),
    ('Amount', "Amount")

)
payment_methods = (
    ('cash', "cash"),
    ('cheque', "cheque"),
    ('bank transfer', "bank transfer"),
    ('paytabs', "paytabs"),

)
payment_status = (
    ('incomplete', "incomplete"),
    ('complete', "complete"),
    ('pending', "pending"),
    ('failed', "failed"),

)
Shipping_details = (
    ('auto', "auto"),
    ("don't show", "don't show"),
)


class SaleInvoice(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey("Users.Customers", db_column='customer',
                                 on_delete=models.CASCADE,
                                 related_name='SaleInvoice_customer')
    sold_by = models.ForeignKey("Users.Employees", db_column='sold_by', on_delete=models.SET(get_deleted_employee),
                                related_name='SaleInvoice_employee')
    warehouse = models.ForeignKey('Store.Warehouses', db_column='warehouse', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    discount = models.IntegerField(null=True, blank=True)
    discount_type = models.CharField(null=True, blank=True, choices=discount_types, max_length=20)
    paid = models.BooleanField(default=False)
    shipping_fees = models.SmallIntegerField(null=True, blank=True)
    shipping_details = models.CharField(max_length=20, choices=Shipping_details)
    notes = models.TextField(null=True, blank=True)
    payment_terms = models.SmallIntegerField(null=True, blank=True)
    total = models.FloatField()
    date = models.DateField(null=True, blank=True)


class Attachments(models.Model):
    id = models.AutoField(primary_key=True)
    sale_invoice = models.ForeignKey(SaleInvoice, db_column='purchase_invoice', on_delete=models.CASCADE,
                                     related_name="Attachments")
    attachment = models.FileField(upload_to='sales/%y/%m')


class SaleInvoice_products(models.Model):
    id = models.AutoField(primary_key=True)
    sales_invoice = models.ForeignKey(SaleInvoice, db_column='sales_invoice', on_delete=models.CASCADE,
                                      related_name="SaleInvoice_products")
    product = models.ForeignKey('Store.Products', db_column='product', on_delete=models.PROTECT, related_name="SaleInvoice")
    quantity = models.SmallIntegerField()
    unit_price = models.SmallIntegerField()
    count_after = models.SmallIntegerField()
    tax1 = models.ForeignKey("Users.Tax", null=True, blank=True, db_column='tax1', on_delete=models.PROTECT,
                             related_name='saleseInvoice_tax')
    tax2 = models.ForeignKey("Users.Tax", null=True, blank=True, db_column='tax2', on_delete=models.PROTECT)


class SalePayments(models.Model):
    id = models.AutoField(primary_key=True)
    Collected_by = models.ForeignKey("Users.Employees", db_column='Collected_by', on_delete=models.SET(get_deleted_employee),
                                     related_name="SalePayments_user")
    method = models.CharField(choices=payment_methods, max_length=20)
    ref_no = models.SmallIntegerField()
    Date = models.DateTimeField(auto_now_add=True)
    payment_details = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='sales/%y/%m', null=True, blank=True)
    Amount = models.IntegerField()
    status = models.CharField(choices=payment_status, default='completed', max_length=20)
    sales_invoice = models.ForeignKey(SaleInvoice, db_column='sales_invoice', on_delete=models.CASCADE,
                                      related_name="SalePayments")
    manual = models.BooleanField(default=False)
