from django.db import models


class Warehouses(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    address = models.CharField(max_length=50, null=True)


class Brands(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)


# TODO on delete product
# TODO function mini_count
class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField(null=True, blank=True)
    supplier = models.ForeignKey("Users.Suppliers", db_column='supplier', related_name='supplier',
                                 on_delete=models.CASCADE)
    # TODO barcode
    selling_price = models.SmallIntegerField(null=True, blank=True)
    purchasing_price = models.SmallIntegerField(null=True, blank=True)
    mini_selling_price = models.SmallIntegerField(null=True, blank=True)
    mini_count = models.SmallIntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    deactivate = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    brand = models.ForeignKey(Brands, db_column='brand', on_delete=models.CASCADE, related_name="Brand", null=True,
                              blank=True)

    def product_count_status(self, product):
        products = Product_count.objects.filter(product_id=product)
        sum = 0
        for item in products:
            sum += item.count
        if sum == 0:
            return "out of stock"
        else:
            return f"in stock {sum}"

    def product_count(self, product):
        products = Product_count.objects.filter(product_id=product)
        sum = 0
        for item in products:
            sum += item.count
        return sum



class Product_count(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE, related_name="Product_count")
    warehouse = models.ForeignKey(Warehouses, db_column='warehouse', on_delete=models.CASCADE)
    count = models.SmallIntegerField()


class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)


class ProductsCategory(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE, related_name="Category")
    category = models.ForeignKey(Categories, db_column='category', on_delete=models.CASCADE, related_name="Category")


class OutPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    warehouse = models.ForeignKey(Warehouses, db_column='warehouse', on_delete=models.CASCADE)
    add_by = models.ForeignKey("Users.Employees", db_column='add_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField()


class OutPermissions_Products(models.Model):

    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE,related_name= "OutPermissions_Products")
    out_permission = models.ForeignKey(OutPermissions, db_column='out_permission', on_delete=models.CASCADE,related_name="OutPermissions_Products")
    quantity = models.SmallIntegerField()
    unit_price = models.SmallIntegerField()
    count_after = models.SmallIntegerField()


class AddPermissions(models.Model):
    id = models.AutoField(primary_key=True)
    warehouse = models.ForeignKey(Warehouses, db_column='warehouse', on_delete=models.CASCADE)
    add_by = models.ForeignKey("Users.Employees", db_column='add_by', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField()


class AddPermissions_Products(models.Model):
    product = models.ForeignKey(Products, db_column='product', on_delete=models.CASCADE,related_name="AddPermissions_Products")
    add_permission = models.ForeignKey(AddPermissions, db_column='add_permission', on_delete=models.CASCADE ,related_name="AddPermissions_Products")
    quantity = models.SmallIntegerField()
    unit_price = models.SmallIntegerField()
    count_after = models.SmallIntegerField()
