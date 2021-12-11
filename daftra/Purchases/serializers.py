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


class PurchaseInvoice_productsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoice_products
        fields = ['id', 'quantity', 'unit_price', 'count_after', 'product', 'tax1', 'tax2']

    def create(self, validated_data, invoice, warehouse):
        for item in validated_data:
            product = PurchaseInvoice_products.objects.create(purchase_invoice=invoice,
                                                              quantity=item.pop('quantity'),
                                                              unit_price=item.pop('unit_price'),
                                                              count_after=item.pop('count_after'),
                                                              product_id=item.pop('product'),
                                                              tax1_id=item.pop('tax1'),
                                                              tax2_id=item.pop('tax2'),
                                                              )
            # change product count
            product_count(operation="+", product=product.product, quantity=product.quantity, warehouse=warehouse)
            # create history record
            add_record_history(activity_type="receive_product",
                               purchase=invoice,
                               add_by=invoice.add_by,
                               activity_id=product.id,
                               product=product.product
                               )
        return invoice


class PurchaseAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = ['id', 'attachment']

    def create(self, validated_data, invoice):
        for item in validated_data:
            Attachments.objects.create(purchase_invoice=invoice,
                                       attachment=item.pop('attachment'),
                                       )


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    PurchaseInvoice_products = PurchaseInvoice_productsSerializer(many=True, read_only=True)
    Attachments = PurchaseAttachmentsSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = ['supplier', 'add_by', 'warehouse', 'discount', 'discount_type', 'paid', 'Received', 'shipping_fees',
                  'notes', 'payment_terms', 'payment_method', 'payment_no', 'total',
                  'PurchaseInvoice_products', 'Attachments']

    def create(self, validated_data, user):
        products = validated_data.pop('PurchaseInvoice_products')
        attachment = validated_data.pop("Attachments")

        invoice = PurchaseInvoice.objects.create(supplier_id=validated_data.pop('supplier'),
                                                 warehouse_id=validated_data.pop('warehouse'),
                                                 discount=validated_data.pop('discount'),
                                                 discount_type=validated_data.pop('discount_type'),
                                                 paid=validated_data.pop('paid'),
                                                 Received=validated_data.pop('Received'),
                                                 shipping_fees=validated_data.pop('shipping_fees'),
                                                 notes=validated_data.pop('notes'),
                                                 payment_terms=validated_data.pop('payment_terms'),
                                                 payment_method=validated_data.pop('payment_method'),
                                                 payment_no=validated_data.pop('payment_no'),
                                                 total=validated_data.pop('total'),
                                                 add_by=user,
                                                 )
        PurchaseInvoice_productsSerializer.create(PurchaseInvoice_productsSerializer(), validated_data=products,
                                                  invoice=invoice, warehouse=invoice.warehouse)
        PurchaseAttachmentsSerializer.create(PurchaseAttachmentsSerializer(), validated_data=attachment,
                                             invoice=invoice)

        # create history record
        add_record_history(activity_type="create_purchase",
                           purchase=invoice,
                           add_by=invoice.add_by,
                           activity_id=invoice.id,
                           )
        return invoice

    def update(self, instance, validated_data):
        # update Invoice instance
        instance.supplier_id = validated_data.get('supplier', instance.supplier_id)
        instance.payment_terms = validated_data.get('payment_terms', instance.payment_terms)
        instance.payment_method = validated_data.get('payment_method', instance.payment_method)
        instance.payment_no = validated_data.get('payment_no', instance.payment_no)
        instance.total = validated_data.get('total', instance.total)
        instance.warehouse_id = validated_data.get('warehouse', instance.warehouse_id)
        instance.discount = validated_data.get('discount', instance.discount)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.discount_type = validated_data.get('discount_type', instance.discount_type)
        instance.paid = validated_data.get('paid', instance.paid)
        instance.Received = validated_data.get('Received', instance.Received)
        instance.shipping_fees = validated_data.get('shipping_fees', instance.shipping_fees)
        instance.save()

        # FOR CHECK IF USER DELETE ANY ITEM
        products = validated_data.get('PurchaseInvoice_products')
        product_ids = [item['id'] for item in products]
        for product in instance.PurchaseInvoice_products.all():
            if product.id not in product_ids:
                # check if there is enough products to Restore
                product_count(operation=">", product=product.product, quantity=product.quantity, warehouse=instance.warehouse)

                deleted_product = deletedActivities.objects.create(item_count=product.quantity,
                                                                   store_count=product.count_after - product.quantity,
                                                                   amount=product.unit_price,
                                                                   product=product.id
                                                                   )
                add_record_history(activity_type="delete_product_invoice",
                                   purchase=instance,
                                   add_by=instance.add_by,
                                   activity_id=deleted_product.id,
                                   product=product.product
                                   )
                # change store count
                product_count(operation="-", product=product.product, quantity=product.quantity,
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
                product_obj = PurchaseInvoice_products.objects.get(product_id=item["product"],
                                                                   purchase_invoice=instance)
                # change product count
                quantity = item.get('quantity')
                # check id quantity is enough
                if quantity < product_obj.quantity:
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

                # create history record
                add_record_history(activity_type="update_product_invoice",
                                   purchase=instance,
                                   add_by=instance.add_by,
                                   activity_id=deleted_product.id,
                                   product=product.product
                                   )
            except ObjectDoesNotExist:
                product = PurchaseInvoice_products.objects.create(purchase_invoice=instance,
                                                                  quantity=item.pop('quantity'),
                                                                  unit_price=item.pop('unit_price'),
                                                                  count_after=item.pop('count_after'),
                                                                  product_id=item.pop('product'),
                                                                  tax1_id=item.pop('tax1'), tax2_id=item.pop('tax2'),
                                                                  )
                # change product count
                product_count(operation="+", product=product.product, quantity=product.quantity,
                              warehouse=instance.warehouse)

                # create history record
                add_record_history(activity_type="receive_product", purchase=instance, add_by=instance.add_by,
                                   activity_id=product.id, product=product.product)
        # update and create  attachments
        for item in attachments:
            try:
                attachment_obj = Attachments.objects.get(pk=item.pop('id'))
                attachment_obj.attachment = item.pop('attachment')
                attachment_obj.save()
            except ObjectDoesNotExist:
                Attachments.objects.create(purchase_invoice=instance, attachment=item.pop('attachment'))

        # create history record
        add_record_history(activity_type="update_invoice",
                           purchase=instance,
                           add_by=instance.add_by,
                           activity_id=instance.id,
                           )

        return validated_data








class paymentsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = PurchasePayments
        fields = ["id", "method", "ref_no", "Date", "status", "employee_name", "manual", "Amount"]

    def get_employee_name(self, obj):
        user = obj.Collected_by.user
        return user.first_name + " " + user.last_name


class paymentsInvoiceSerializer(serializers.ModelSerializer):
    PurchasePayments = paymentsSerializer(many=True, read_only=True)

    class Meta:
        model = PurchaseInvoice
        fields = ["total", "PurchasePayments"]


class paymentDetailsSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = PurchasePayments
        fields = ["id", "method", "ref_no", "Date", "status", "Amount", "employee_name", 'user']

    def get_user(self, obj):
        user = obj.purchase_.customer.user
        data = {
            "supplier": user.first_name + " " + user.last_name,
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
        model = PurchasePayments
        fields = ["id", "payment_details", "notes", "attachment", "purchase_invoice",
                  "method", "ref_no", "status", "Collected_by", "Amount"]


class InvoiceStoreSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseInvoice_products
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
