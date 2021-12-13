from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from rest_framework.response import Response
from .models import *
from Users.models import *
from Store.models import *


def add_record_history(activity_type, activity_id, add_by, product=None, customer=None, employee=None, sale=None,
                       outpermissions=None, addpermissions=None, purchase=None):
    RecordHistory.objects.create(
        type=activity_type,
        activity_id=activity_id,
        product=product,
        customer=customer,
        employee=employee,
        sale=sale,
        purchase=purchase,
        add_by=add_by,
        outPermissions=outpermissions,
        addPermissions=addpermissions,
    )


# TODO change all products count after update or delete product

def product_count(operation, product, quantity, warehouse):
    product_obj = Product_count.objects.get(product=product, warehouse=warehouse)
    if operation == "+":
        product_obj.count += quantity
        product_obj.save()

    elif operation == "-":
        product_obj.count -= quantity
        product_obj.save()
    elif product_obj.count < quantity:
        raise serializers.ValidationError(f"product {product_obj.product.name} did not have enough quantity ")


class SaleInvoice_productsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleInvoice_products
        fields = ['id', 'quantity', 'unit_price', 'count_after', 'product', 'tax1', 'tax2']

    def create(self, validated_data, invoice, warehouse):
        for item in validated_data:
            product = SaleInvoice_products.objects.create(sales_invoice=invoice,
                                                          quantity=item.pop('quantity'),
                                                          unit_price=item.pop('unit_price'),
                                                          count_after=item.pop('count_after'),
                                                          product_id=item.pop('product'),
                                                          tax1_id=item.pop('tax1'),
                                                          tax2_id=item.pop('tax2'),
                                                          )
            # change product count
            product_count(operation="-", product=product.product, quantity=product.quantity, warehouse=warehouse)
            # create history record
            add_record_history(activity_type="sold_product",
                               sale=invoice,
                               add_by=invoice.sold_by,
                               activity_id=product.id,
                               product=product.product
                               )


class SaleAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = ['id', 'attachment']

    def create(self, validated_data, invoice):
        for item in validated_data:
            Attachments.objects.create(sale_invoice=invoice,
                                       attachment=item.pop('attachment'),
                                       )


class SaleInvoiceSerializer(serializers.ModelSerializer):
    SaleInvoice_products = SaleInvoice_productsSerializer(many=True, read_only=True)
    Attachments = SaleAttachmentsSerializer(many=True, read_only=True)

    class Meta:
        model = SaleInvoice
        fields = ['customer', 'warehouse', 'discount', 'discount_type', 'paid', 'shipping_fees', 'shipping_details',
                  'notes', 'payment_terms', 'payment_method', 'payment_no', 'total', 'date', 'SaleInvoice_products',
                  'Attachments', 'sold_by']

    def create(self, validated_data, user):
        products = validated_data.pop('SaleInvoice_products')
        attachment = validated_data.pop("Attachments")

        # change product count
        for item in products:
            product = Products.objects.get(pk=item["product"])
            warehouse = Warehouses.objects.get(pk=validated_data.get('warehouse'))
            product_count(operation=">", product=product, quantity=item["quantity"], warehouse=warehouse)

        invoice = SaleInvoice.objects.create(customer_id=validated_data.pop('customer'),
                                             warehouse_id=validated_data.pop('warehouse'),
                                             discount=validated_data.pop('discount'),
                                             discount_type=validated_data.pop('discount_type'),
                                             paid=validated_data.pop('paid'),
                                             shipping_fees=validated_data.pop('shipping_fees'),
                                             shipping_details=validated_data.pop('shipping_details'),
                                             notes=validated_data.pop('notes'),
                                             payment_terms=validated_data.pop('payment_terms'),
                                             payment_method=validated_data.pop('payment_method'),
                                             payment_no=validated_data.pop('payment_no'),
                                             total=validated_data.pop('total'),
                                             sold_by=user,
                                             date =validated_data.pop("date")
                                             )
        SaleInvoice_productsSerializer.create(SaleInvoice_productsSerializer(), validated_data=products,
                                              invoice=invoice, warehouse=invoice.warehouse)
        SaleAttachmentsSerializer.create(SaleAttachmentsSerializer(), validated_data=attachment, invoice=invoice)

        # create history record
        add_record_history(activity_type="create_sale",
                           sale=invoice,
                           add_by=invoice.sold_by,
                           activity_id=invoice.id,
                           )
        return invoice

    def update(self, instance, validated_data):
        # update Invoice instance
        instance.customer_id = validated_data.get('customer', instance.customer_id)
        instance.payment_terms = validated_data.get('payment_terms', instance.payment_terms)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.payment_no = validated_data.get('payment_no', instance.payment_no)
        instance.total = validated_data.get('total', instance.total)
        instance.warehouse_id = validated_data.get('warehouse', instance.warehouse_id)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.discount_type = validated_data.get('discount_type', instance.discount_type)
        instance.paid = validated_data.get('paid', instance.paid)
        instance.date = validated_data.get('date', instance.date)
        instance.shipping_fees = validated_data.get('shipping_fees', instance.shipping_fees)
        instance.shipping_details = validated_data.get('shipping_details', instance.shipping_details)
        instance.save()

        # FOR CHECK IF USER DELETE ANY ITEM
        products = validated_data.get('SaleInvoice_products')
        product_ids = [item['product'] for item in products]
        for product in instance.SaleInvoice_products.all():
            if product.id not in product_ids:
                deleted_product = deletedActivities.objects.create(
                    item_count=product.quantity,
                    store_count=product.quantity + product.count_after,
                    amount=product.unit_price,
                    product=product.id
                )
                add_record_history(activity_type="delete_product_invoice",
                                   sale=instance,
                                   add_by=instance.sold_by,
                                   activity_id=deleted_product.id,
                                   product=product.product
                                   )
                #
                product_count(operation="+", product=product.product, quantity=product.quantity,
                              warehouse=instance.warehouse)
                product.delete()

        # FOR CHECK IF USER DELETE ANY ATTACHMENT
        attachments = validated_data.get('Attachments')
        attachment_ids = [item['id'] for item in attachments]
        for Attachment in instance.Attachments.all():
            if Attachment.id not in attachment_ids:
                Attachment.delete()

        # update and create  products
        for item in products:
            try:
                product_obj = SaleInvoice_products.objects.get(product_id=item["product"], sales_invoice=instance)
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
                product_obj.quantity = item.get('quantity')
                product_obj.count_after = item.pop('count_after')
                product_obj.unit_price = item.pop('unit_price')
                product_obj.product_id = item.pop('product')
                product_obj.tax1_id = item.pop('tax1')
                product_obj.tax2_id = item.pop('tax2')
                product_obj.save()
                add_record_history(activity_type="update_product_invoice",
                                   sale=instance,
                                   add_by=instance.sold_by,
                                   activity_id=product_obj.id,
                                   product=product_obj.product
                                   )
            except ObjectDoesNotExist:
                # TODO put change product before add
                product = SaleInvoice_products.objects.create(sales_invoice=instance,
                                                              quantity=item.pop('quantity'),
                                                              unit_price=item.pop('unit_price'),
                                                              count_after=item.pop('count_after'),
                                                              product_id=item.pop('product'),
                                                              tax1_id=item.pop('tax1'),
                                                              tax2_id=item.pop('tax2'),
                                                              )
                # change product count

                product_count(operation=">", product=product.product, quantity=product.quantity,
                              warehouse=instance.warehouse)
                product_count(operation="-", product=product.product, quantity=product.quantity,
                              warehouse=instance.warehouse)

                # create history record
                add_record_history(activity_type="sold_product",
                                   sale=instance,
                                   add_by=instance.sold_by,
                                   activity_id=product.id,
                                   product=product.product
                                   )
        # update and create  attachments
        for item in attachments:
            try:
                attachment_obj = Attachments.objects.get(pk=item.pop('id'))
                attachment_obj.attachment = item.pop('attachment')
                attachment_obj.save()
            except ObjectDoesNotExist:
                Attachments.objects.create(sales_invoice=instance, attachment=item.pop('attachment')
                                           )

        # create history record
        add_record_history(activity_type="update_invoice",
                           sale=instance,
                           add_by=instance.sold_by,
                           activity_id=instance.id,
                           )

        return validated_data


class paymentsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = SalePayments
        fields = ["id", "method", "ref_no", "Date", "status", "employee_name", "manual", "Amount"]

    def get_employee_name(self, obj):
        user = obj.Collected_by.user
        return user.first_name + " " + user.last_name


class paymentsInvoiceSerializer(serializers.ModelSerializer):
    SalePayments = paymentsSerializer(many=True, read_only=True)

    class Meta:
        model = SaleInvoice
        fields = ["total", "SalePayments"
                  ]


class paymentDetailsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = SalePayments
        fields = ["id", "method", "ref_no", "Date", "status", "Amount", "employee_name", 'user']

    def get_user(self, obj):
        user = obj.sales_invoice.customer.user
        data = {
            "customer": user.first_name + " " + user.last_name,
            "phone": user.phone,
            "country": user.country,
            "city": user.city,
            "address": user.address,
            "postal_code": user.postal_code,

        }
        return data

    def get_employee_name(self, obj):
        user = obj.Collected_by.user
        return user.first_name + " " + user.last_name


class CreateUpdatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalePayments
        fields = ["id", "payment_details", "notes", "attachment", "sales_invoice",
                  "method", "ref_no", "status", "Collected_by", "manual", "Amount"]


class InvoiceStoreSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = SaleInvoice_products
        fields = ["quantity", 'count_after', 'product_details']

    def get_product_details(self, obj):
        product = obj.product
        data = {
            "name": product.name,
            "id": product.id
        }
        return data

    def to_representation(self, instance):
        data = super(InvoiceStoreSerializer, self).to_representation(instance)
        product = data.pop('product_details')
        for key, val in product.items():
            data.update({key: val})
        return data
