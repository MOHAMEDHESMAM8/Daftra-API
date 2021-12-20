from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.response import Response
from .models import *
from Users.models import *
from Store.models import *
from Sales.serializers import product_count, add_record_history


class ProductCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_count
        fields = ["warehouse", "count"]

    def create(self, validated_data, product):
        for item in validated_data:
            Product_count.objects.create(
                product=product,
                warehouse_id=item.pop('warehouse'),
                count=item.pop('count')
            )
        return validated_data


class ProductCategorySerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField()

    class Meta:
        model = ProductsCategory
        fields = ['category_id']

    def get_category_id(self, obj):
        return obj.category.id

    def create(self, product, validated_data):
        for item in validated_data:
            category_id = item.pop('category_id')
            if category_id != 0:
                category_id = item.pop('category_id')
                ProductsCategory.objects.create(
                    product=product,
                    category_id=category_id,
                )
            else:
                category = Categories.objects.create(name=item.pop('category_name'))
                ProductsCategory.objects.create(
                    product=product,
                    category=category,
                )
        return validated_data


class ProductSerializer(serializers.ModelSerializer):
    Product_count = ProductCountSerializer(many=True, read_only=True)
    Category = ProductCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Products
        fields = ["id", "name", "description", "supplier", "selling_price", "purchasing_price", "mini_selling_price",
                  "mini_count", "notes", "brand", "barcode", "deactivate", "Product_count", "Category"]

    def create(self, validated_data):
        product = Products.objects.create(supplier_id=validated_data.pop("supplier"),
                                          brand_id=validated_data.pop("brand"),
                                          name=validated_data.pop("name"),
                                          description=validated_data.pop("description"),
                                          selling_price=validated_data.pop("selling_price"),
                                          purchasing_price=validated_data.pop("purchasing_price"),
                                          mini_selling_price=validated_data.pop("mini_selling_price"),
                                          mini_count=validated_data.pop("mini_count"),
                                          notes=validated_data.pop("notes"),
                                          barcode=validated_data.pop("barcode"),
                                          deactivate=validated_data.pop("deactivate"),
                                          )
        category = validated_data.get("Category")
        ProductCategorySerializer.create(ProductCategorySerializer(), product=product, validated_data=category)

        try:
            products = validated_data.pop("Product_count")
            ProductCountSerializer.create(ProductCountSerializer(), validated_data=products, product=product)
        except KeyError:
            pass
        return validated_data

    def update(self, instance, validated_data):
        instance.name = validated_data.pop("name")
        instance.supplier_id = validated_data.pop("supplier")
        instance.selling_price = validated_data.pop("selling_price")
        instance.purchasing_price = validated_data.pop("purchasing_price")
        instance.mini_selling_price = validated_data.pop("mini_selling_price")
        instance.mini_count = validated_data.pop("mini_count")
        instance.notes = validated_data.pop("notes")
        instance.brand_id = validated_data.pop("brand")
        instance.barcode = validated_data.pop("barcode")
        instance.deactivate = validated_data.pop("deactivate")
        instance.save()

        categories = validated_data.get("Category")
        # delete categories
        category_ids = [item['category_id'] for item in categories]
        for category in instance.Category.all():
            if category.category.id not in category_ids:
                category.delete()
        # add unexists category
        for item in categories:
            try:
                ProductsCategory.objects.get(category_id=item.get("category_id"), product=instance)
            except ObjectDoesNotExist:
                category_id = item.get('category_id')
                if category_id != 0:
                    category_id = item.get('category_id')
                    ProductsCategory.objects.create(
                        product=instance,
                        category_id=category_id,
                    )
                else:
                    category = Categories.objects.create(name=item.pop('category_name'))
                    ProductsCategory.objects.create(
                        product=instance,
                        category=category,
                    )
        return instance


# TODO add update product record history and permissions and product store


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Brands
        fields = '__all__'


class OutPermissionsProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutPermissions_Products
        fields = ["product", "quantity", "count_after", "unit_price"]

    def create(self, validated_data, permission):
        for item in validated_data:
            obj = OutPermissions_Products.objects.create(
                product_id=item.pop("product"),
                quantity=item.pop("quantity"),
                count_after=item.pop("count_after"),
                unit_price=item.pop("unit_price"),
                out_permission=permission
            )
            # change product count
            product_count(operation="-", product=obj.product, quantity=obj.quantity,
                          warehouse=obj.out_permission.warehouse)
            # add record history
            add_record_history(activity_type="product_outPermission",
                               add_by=obj.out_permission.add_by,
                               activity_id=obj.id,
                               product=obj.product,
                               outpermissions=permission
                               )


class OutPermissionsSerializer(serializers.ModelSerializer):
    OutPermissions_Products = OutPermissionsProductsSerializer(many=True, read_only=True)

    class Meta:
        model = OutPermissions
        fields = ["warehouse", "notes", "OutPermissions_Products"]

    def create(self, validated_data, user):
        products = validated_data.pop("OutPermissions_Products")
        if not products:
            raise serializers.ValidationError("you should add products")
        permission = OutPermissions.objects.create(
            warehouse_id=validated_data.pop("warehouse"),
            add_by=user,
            notes=validated_data.pop("notes"),
        )
        OutPermissionsProductsSerializer.create(OutPermissionsProductsSerializer(), validated_data=products,
                                                permission=permission)

        add_record_history(activity_type="add_outPermission",
                           add_by=user,
                           activity_id=permission.id,
                           outpermissions=permission
                           )

        return permission

    def update(self, instance, validated_data, user):
        instance.warehouse_id = validated_data.pop("warehouse", instance.warehouse_id)
        instance.notes = validated_data.pop("notes", instance.notes)
        instance.save()

        products = validated_data.get("OutPermissions_Products")
        product_ids = [item['product'] for item in products]
        for product in instance.OutPermissions_Products.all():
            if product.product.id not in product_ids:
                # add deleted quantity to product
                product_count(operation="+", product=product.product, quantity=product.quantity,
                              warehouse=instance.warehouse)
                # add delete record
                deleted_product = deletedActivities.objects.create(
                    item_count=product.quantity,
                    store_count=product.quantity + product.count_after,
                    amount=product.unit_price,
                    product=product.id
                )
                # add record history
                add_record_history(activity_type="delete_product_outPermission",
                                   add_by=user,
                                   activity_id=deleted_product.id,
                                   product=product.product,
                                   outpermissions=instance
                                   )
                product.delete()
        # update or create  products
        for item in products:
            try:
                product_obj = OutPermissions_Products.objects.get(product_id=item.get('product'),
                                                                  out_permission=instance)
                # change product count
                quantity = item.get('quantity')

                # check id quantity is enough
                if quantity > product_obj.quantity:
                    sub = quantity - product_obj.quantity
                    product_count(operation=">", product=product_obj.product, quantity=sub,
                                  warehouse=instance.warehouse)
                    product_count(operation="-", product=product_obj.product, quantity=sub,
                                  warehouse=instance.warehouse)
                else:
                    sub = product_obj.quantity - quantity
                    product_count(operation="+", product=product_obj.product, quantity=sub,
                                  warehouse=instance.warehouse)
                # update product
                product_obj.quantity = item.get('quantity')
                product_obj.count_after = item.get('count_after')
                product_obj.unit_price = item.get('unit_price')
                product_obj.product_id = item.get('product')
                product_obj.save()
                # add record history
                add_record_history(activity_type="update_product_outPermission",
                                   add_by=instance.add_by,
                                   activity_id=product_obj.id,
                                   product=product_obj.product,
                                   outpermissions=instance
                                   )
            except ObjectDoesNotExist:
                product_obj = Products.objects.get(id=item.get("product"))
                # check if there is enough products
                product_count(operation=">", product=product_obj, quantity=item.get("quantity"),
                              warehouse=instance.warehouse)
                # add new product to permission
                obj = OutPermissions_Products.objects.create(product_id=item.pop("product"),
                                                             quantity=item.pop("quantity"),
                                                             count_after=item.pop("count_after"),
                                                             unit_price=item.pop("unit_price"),
                                                             out_permission=instance
                                                             )
                # change product count
                product_count(operation="-", product=obj.product, quantity=obj.quantity,
                              warehouse=instance.warehouse)
                # add record history
                add_record_history(activity_type="add_product_outPermission",
                                   add_by=user,
                                   activity_id=product_obj.id,
                                   product=product_obj,
                                   outpermissions=instance
                                   )
        # create history record
        add_record_history(activity_type="update_outPermission",
                           add_by=user,
                           activity_id=instance.id,
                           outpermissions=instance
                           )

        return instance


class AddPermissionsProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddPermissions_Products
        fields = ["product", "quantity", "count_after", "unit_price"]

    def create(self, validated_data, permission):
        for item in validated_data:
            obj = AddPermissions_Products.objects.create(
                product_id=item.pop("product"),
                quantity=item.pop("quantity"),
                count_after=item.pop("count_after"),
                unit_price=item.pop("unit_price"),
                add_permission=permission
            )
            product_count(operation="+", product=obj.product, quantity=obj.quantity,
                          warehouse=obj.add_permission.warehouse)
            # add record history
            add_record_history(activity_type="product_addPermission",
                               add_by=obj.add_permission.add_by,
                               activity_id=obj.id,
                               product=obj.product,
                               addpermissions=permission
                               )


class AddPermissionsSerializer(serializers.ModelSerializer):
    AddPermissions_Products = AddPermissionsProductsSerializer(many=True, read_only=True)

    class Meta:
        model = AddPermissions
        fields = ["warehouse", "notes", "AddPermissions_Products"]

    def create(self, validated_data, user):
        products = validated_data.pop("AddPermissions_Products")
        if not products:
            raise serializers.ValidationError("you should add products")

        permission = AddPermissions.objects.create(
            warehouse_id=validated_data.pop("warehouse"),
            add_by=user,
            notes=validated_data.pop("notes"),
        )
        AddPermissionsProductsSerializer.create(AddPermissionsProductsSerializer(), validated_data=products,
                                                permission=permission)

        # add record history
        add_record_history(activity_type="add_addPermission",
                           add_by=user,
                           activity_id=permission.id,
                           addpermissions=permission
                           )
        return permission

    def update(self, instance, validated_data, user):
        instance.warehouse_id = validated_data.pop("warehouse", instance.warehouse_id)
        instance.notes = validated_data.pop("notes", instance.notes)
        instance.save()

        products = validated_data.get("AddPermissions_Products")
        product_ids = [item['product'] for item in products]
        for product in instance.AddPermissions_Products.all():
            if product.product.id not in product_ids:
                # add deleted quantity to product
                product_count(operation="+", product=product.product, quantity=product.quantity,
                              warehouse=instance.warehouse)
                # add delete record
                deleted_product = deletedActivities.objects.create(
                    item_count=product.quantity,
                    store_count=product.quantity + product.count_after,
                    amount=product.unit_price,
                    product=product.id
                )
                # add record history
                add_record_history(activity_type="delete_product_addPermission",
                                   add_by=user,
                                   activity_id=deleted_product.id,
                                   product=product.product,
                                   addpermissions=instance
                                   )
                product.delete()

        # update or create  products
        for item in products:
            try:
                product_obj = AddPermissions_Products.objects.get(product_id=item.get('product'),
                                                                  add_permission=instance)
                # change product count
                quantity = item.get('quantity')

                # check id quantity is enough
                if quantity > product_obj.quantity:
                    sub = quantity - product_obj.quantity
                    product_count(operation=">", product=product_obj.product, quantity=sub,
                                  warehouse=instance.warehouse)
                    product_count(operation="-", product=product_obj.product, quantity=sub,
                                  warehouse=instance.warehouse)
                else:
                    sub = product_obj.quantity - quantity
                    product_count(operation="+", product=product_obj.product, quantity=sub,
                                  warehouse=instance.warehouse)
                # update product
                product_obj.quantity = item.get('quantity')
                product_obj.count_after = item.get('count_after')
                product_obj.unit_price = item.get('unit_price')
                product_obj.product_id = item.get('product')
                product_obj.save()
                # add record history
                add_record_history(activity_type="update_product_addPermission",
                                   add_by=user,
                                   activity_id=product_obj.id,
                                   product=product_obj.product,
                                   addpermissions=instance
                                   )
            except ObjectDoesNotExist:
                product_obj = Products.objects.get(id=item.get("product"))
                # check if there is enough products
                product_count(operation=">", product=product_obj, quantity=item.get("quantity"),
                              warehouse=instance.warehouse)
                # add new product to permission
                obj = AddPermissions_Products.objects.create(product_id=item.pop("product"),
                                                             quantity=item.pop("quantity"),
                                                             count_after=item.pop("count_after"),
                                                             unit_price=item.pop("unit_price"),
                                                             add_permission=instance
                                                             )
                # change product count
                product_count(operation="-", product=obj.product, quantity=obj.quantity,
                              warehouse=instance.warehouse)
                # add record history
                add_record_history(activity_type="add_product_addPermission",
                                   add_by=user,
                                   activity_id=product_obj.id,
                                   product=product_obj,
                                   addpermissions=instance
                                   )
        # create history record
        add_record_history(activity_type="update_addPermission",
                           add_by=user,
                           activity_id=instance.id,
                           addpermissions=instance
                           )

        return instance
