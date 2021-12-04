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


class PurchaseInvoice(models.Model):
    id = models.AutoField(primary_key=True)
    supplier = models.ForeignKey("Users.Suppliers", db_column='supplier',
                                 on_delete=models.CASCADE)
    add_by = models.ForeignKey("Users.Employees", db_column='add_by', on_delete=models.CASCADE)
    warehouse = models.ForeignKey('Store.Warehouses', db_column='warehouse', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    Update_at = models.DateTimeField(auto_now=True)
    payment_terms = models.SmallIntegerField(null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)
    discount_type = models.CharField(null=True, blank=True, choices=discount_types, max_length=20)
    paid = models.BooleanField(default=False)
    shipping_fees = models.SmallIntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    payment_method = models.CharField(choices=payment_methods, default='cash', max_length=20)
    payment_no = models.IntegerField(null=True, blank=True)
    Received = models.BooleanField(default=False)
    total = models.FloatField()


class Attachments(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_invoice = models.ForeignKey(PurchaseInvoice, db_column='purchase_invoice', on_delete=models.CASCADE,
                                         related_name="Attachments")
    attachment = models.FileField(upload_to='Purchases/%y/%m')


# TODO unique product and invoice (double key) (in sales also)
class PurchaseInvoice_products(models.Model):
    id = models.AutoField(primary_key=True)
    purchase_invoice = models.ForeignKey(PurchaseInvoice, db_column='purchase_invoice', on_delete=models.CASCADE,
                                         related_name="PurchaseInvoice_products")
    product = models.ForeignKey('Store.Products', db_column='product', on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.SmallIntegerField()
    count_after = models.SmallIntegerField()
    tax1 = models.ForeignKey("Users.Tax", null=True, blank=True, db_column='tax1', on_delete=models.CASCADE,
                             related_name='PurchaseInvoice_tax')
    tax2 = models.ForeignKey("Users.Tax", null=True, blank=True, db_column='tax2', on_delete=models.CASCADE)


class PurchasePayments(models.Model):
    id = models.AutoField(primary_key=True)
    Collected_by = models.ForeignKey("Users.Employees", db_column='Collected_by', on_delete=models.CASCADE)
    method = models.CharField(choices=payment_methods, max_length=20)
    ref_no = models.SmallIntegerField()
    Date = models.DateTimeField(auto_now_add=True)
    payment_details = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    attachment = models.FileField(upload_to='Purchases/%y/%m', null=True, blank=True)
    Amount = models.IntegerField()
    status = models.CharField(choices=payment_status, default='completed', max_length=20)
    purchase_invoice = models.ForeignKey(PurchaseInvoice, db_column='purchase_invoice', on_delete=models.CASCADE,
                                         related_name="PurchasePayments")
