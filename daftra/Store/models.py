from django.db import models


class Warehouses(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=50, null=True)


# TODO on delete product
class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField(null=True)
    supplier = models.ForeignKey("Users.Suppliers", db_column='supplier', related_name='supplier',
                                 on_delete=models.CASCADE)
    # TODO barcode
    selling_price = models.SmallIntegerField()
    purchasing_price = models.SmallIntegerField()
    mini_selling_price = models.SmallIntegerField()
    mini_count = models.SmallIntegerField()
    notes = models.TextField()
    deactivate = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


class Product_count(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouses, db_column='warehouse', on_delete=models.CASCADE)
    count = models.SmallIntegerField()


class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)


class ProductsCategory(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE)
    category = models.ForeignKey(Categories, db_column='category', on_delete=models.CASCADE)


class Brands(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)


class ProductsBrand(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE)
    Brand = models.ForeignKey(Brands, db_column='brand', on_delete=models.CASCADE)


class OutPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    warehouse = models.ForeignKey(Warehouses, db_column='warehouse', on_delete=models.CASCADE)
    add_by = models.ForeignKey("Users.Employees", db_column='add_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField()


class OutPermissions_Products(models.Model):
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE)
    out_permission = models.ForeignKey(OutPermissions, db_column='out_permission', on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    count_after = models.SmallIntegerField()


class AddPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    warehouse = models.ForeignKey(Warehouses, db_column='warehouse', on_delete=models.CASCADE)
    add_by = models.ForeignKey("Users.Employees", db_column='add_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField()


class AddPermissions_Products(models.Model):
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE)
    add_permission = models.ForeignKey(AddPermissions, db_column='add_permission', on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    count_after = models.SmallIntegerField()
