# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from merchant.models import Merchant
from merchant.serializers import MerchantSerializer
from .models import (Brand,
                     Category,
                     Merchandise,
                     Inventory)
from history.models import History


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('id', 'brand', 'in_stock')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'category', 'in_stock')


class MerchandiseSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(many=False, read_only=True)
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Merchandise
        fields = ('id', 'brand', 'category', 'in_stock', 'code',
                  'model', 'certification', 'after_sales', 'spare_parts',
                  'delivery_time', 'remarks')


class InventorySerializer(serializers.ModelSerializer):
    merchandise = MerchandiseSerializer(many=False, read_only=True)
    merchant = MerchantSerializer(many=False, read_only=True)

    class Meta:
        model = Inventory
        fields = ('id', 'merchant', 'quantity', 'merchandise')


class MerchantInventorySerializer(InventorySerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'price', 'quantity', 'merchandise', 'modified_date')


class MerchandiseInventorySerializer(InventorySerializer):
    class Meta:
        model = Inventory
        fields = ('id', 'price', 'quantity', 'merchant', 'modified_date')


class UpdateInvtBaseSerializer(serializers.Serializer):
    current_merchant_id = serializers.CharField(required=True)
    merchandise_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)
    remarks = serializers.CharField(required=False)


class CreateNewInvtSerializer(UpdateInvtBaseSerializer):
    price = serializers.DecimalField(required=True,
                                     max_digits=11, decimal_places=2)

    def create(self):
        try:
            md = Merchandise.objects.get(
                id=self.validated_data['merchandise_id'])
            cm = Merchant.objects.get(
                id=self.validated_data['current_merchant_id'])
        except ObjectDoesNotExist:
            return {"result": "fail"}
        inv = Inventory.objects.create(
            merchandise=md,
            merchant=cm,
            quantity=self.validated_data['quantity'],
            price=self.validated_data['price'],
            remarks=self.validated_data.get('remarks'))

        History.objects.create(
            inventory=inv,
            initiator=cm,
            quantity=self.validated_data['quantity'],
            price=self.validated_data['price'],
            remarks=self.validated_data.get('remarks'))
        return {"result": "create"}


class DepositToInvtSerializer(UpdateInvtBaseSerializer):
    """Merchant增自己的库存"""
    price = serializers.DecimalField(required=False,
                                     max_digits=11, decimal_places=2)

    def deposit(self):
        try:
            cm = Merchant.objects.get(
                id=self.validated_data['current_merchant_id'])
            inv = Inventory.objects.get(
                merchandise=self.validated_data['merchandise_id'],
                merchant=cm)
        except ObjectDoesNotExist:
            return {"result": "fail"}
        prev_quantity = inv.quantity
        if self.validated_data.get("price"):
            inv.price = self.validated_data['price']
        inv.quantity += self.validated_data['quantity']
        inv.remarks = self.validated_data.get('remarks')
        inv.save()

        price = self.validated_data.get('price') or inv.price
        History.objects.create(
            inventory=inv,
            initiator=cm,
            prev_quantity=prev_quantity,
            quantity=self.validated_data['quantity'],
            price=price,
            remarks=self.validated_data.get('remarks'))
        return {"result": "deposit success"}


class WithdrawFromInvtSerializer(UpdateInvtBaseSerializer):
    """Merchant减自己的库存"""

    def withdraw(self):
        try:
            cm = Merchant.objects.get(
                id=self.validated_data['current_merchant_id'])
            inv = Inventory.objects.get(
                merchandise=self.validated_data['merchandise_id'],
                merchant=cm)
        except ObjectDoesNotExist:
            return {"result": "fail", "details": "找不到您的库存"}

        if self.validated_data['quantity'] > inv.quantity:
            return {"result": "fail", "details": "您的库存不足"}
        prev_quantity = inv.quantity
        inv.quantity -= self.validated_data['quantity']
        inv.remarks = self.validated_data.get('remarks')
        inv.save()

        History.objects.create(
            type=1,
            inventory=inv,
            initiator=cm,
            prev_quantity=prev_quantity,
            quantity=self.validated_data['quantity'],
            price=inv.price,
            remarks=self.validated_data.get('remarks'))
        return {"result": "withdraw success"}


class WithdrawFromOthersInvtSerializer(UpdateInvtBaseSerializer):
    """Merchant借其他的库存

    withdraw_from =
    [{"merchant":"83719796-8d17-4709-a12c-c7b56b90d7fb",
      "quantity":1
      },
     {
      "merchant":"b4b33695-983d-4fea-bb51-6822f76f74c2",
      "quantity":2,
      "remarks":"withdraw"
      "deal_price": 20.6
     }
    ]
    """
    withdraw_from = serializers.JSONField(required=True)

    def withdraw(self):
        try:
            cm = Merchant.objects.get(
                id=self.validated_data['current_merchant_id'])
            # 借库存需当前用户无库存或数量为0
            current_inv = Inventory.objects.get(
                merchandise=self.validated_data['merchandise_id'],
                merchant=cm)
            if current_inv.quantity > 0:
                return {"result": "fail", "details": "请先使用自己的配货"}
        except ObjectDoesNotExist:
            pass

        for item in self.validated_data.get('withdraw_from', []):
            if item['merchant'] == self.validated_data['current_merchant_id']:
                return {"result": "fail", "details": "错误的商户信息"}
            try:
                withdraw_inv = Inventory.objects.get(
                    merchandise=self.validated_data['merchandise_id'],
                    merchant=item['merchant'])
            except ObjectDoesNotExist:
                return {"result": "fail", "details": "找不到对应商户的库存"}
            if int(item['quantity']) > withdraw_inv.quantity:
                return {"result": "fail", "details": "对应商户的库存不足"}
            prev_quantity = withdraw_inv.quantity
            withdraw_inv.quantity -= int(item['quantity'])
            withdraw_inv.save()

            deal_price = item.get('deal_price', withdraw_inv.price)
            History.objects.create(
                type=2,
                inventory=withdraw_inv,
                initiator=cm,
                prev_quantity=prev_quantity,
                quantity=int(item['quantity']),
                price=withdraw_inv.price,
                deal_price=deal_price,
                remarks=item.get('remarks'))
        return {"result": "withdraw others success"}
