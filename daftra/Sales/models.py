from django.db import models

# Create your models here.
from django.db import models

discount_types = (
    ('percentage(%)', "percentage"),
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
                               on_delete=models.CASCADE)
    sold_by = models.ForeignKey("Users.Employees", db_column='add_by', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('Store.Warehouses', db_column='warehouse', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    discount = models.IntegerField(null=True, blank=True)
    discount_type = models.CharField(null=True, blank=True, choices=discount_types, max_length=20)
    paid = models.BooleanField(default=False)
    shipping_fees = models.SmallIntegerField(null=True, blank=True)
    shipping_details = models.CharField(max_length=20, choices=Shipping_details)
    notes = models.TextField(null=True, blank=True)
    payment_terms = models.SmallIntegerField(null=True, blank=True)
    payment_method = models.CharField(choices=payment_methods, default='cash', max_length=20)
    payment_no = models.IntegerField(null=True, blank=True)
    total = models.FloatField()


class Attachments(models.Model):
    id = models.AutoField(primary_key=True)
    sale_invoice = models.ForeignKey(SaleInvoice, db_column='purchase_invoice', on_delete=models.CASCADE)
    attachment = models.FileField(upload_to='Files/%y/%m')


class SaleInvoice_products(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_invoice = models.ForeignKey(SaleInvoice, db_column='purchase_invoice', on_delete=models.CASCADE)
    product = models.ForeignKey('Store.Products', db_column='product', on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.SmallIntegerField()
    count_after = models.SmallIntegerField()
    tax1 = models.ForeignKey("Users.Tax",null=True,blank=True,db_column='tax1', on_delete=models.CASCADE,related_name='saleseInvoice_tax')
    tax2 = models.ForeignKey("Users.Tax",null=True,blank=True,db_column='tax2', on_delete=models.CASCADE)


class SalePayments(models.Model):
    id = models.AutoField(primary_key=True)
    Collected_by = models.ForeignKey("Users.Employees", db_column='Collected_by', on_delete=models.CASCADE)
    method = models.CharField(choices=payment_methods, max_length=20)
    ref_no = models.SmallIntegerField()
    Date = models.DateTimeField(auto_now_add=True)
    payment_details = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='Files/%y/%m', null=True, blank=True)
    Amount = models.IntegerField()
    status = models.CharField(choices=payment_status, default='completed', max_length=20)
