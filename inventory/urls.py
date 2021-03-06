# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import (BrandList,
                    CategoryList,
                    MerchandiseList,
                    InventoryList,
                    MerchantInventoryList,
                    MerchandiseInventoryList,
                    create_inventory,
                    deposit_to_inventory,
                    withdraw_from_inventory,
                    withdraw_from_others_inventory,
                    )

app_name = 'inventory'
urlpatterns = [
    # 查询全部 品牌brand/ 品类category/ 商品merchandise
    url(r'^brands', login_required(BrandList.as_view()), name='brand_list'),
    url(r'^categories', login_required(CategoryList.as_view()), name='category_list'),
    url(r'^merchandise', login_required(MerchandiseList.as_view()), name='merchandise_list'),
    # 查询全部 库存inventory
    url(r'^inventories$', login_required(InventoryList.as_view()), name='inventory_list'),
    # 查询某个merchant的库存
    url(r'^inventories/merchants$', login_required(MerchantInventoryList.as_view()), name='merchant_inventory_list'),
    # 查询某个merchandise的库存
    url(r'^inventories/merchandise$', login_required(MerchandiseInventoryList.as_view()), name='merchandise_inventory_list'),
    # 新建库存
    url(r'^create/$', login_required(create_inventory),name='create_inventory'),
    # 增库存
    url(r'^deposit/$', login_required(deposit_to_inventory),name='deposit_to_inventory'),
    # 自减库存
    url(r'^withdraw/$', login_required(withdraw_from_inventory),name='withdraw_from_inventory'),
    # 取用他人库存
    url(r'^withdraw/others/$', login_required(withdraw_from_others_inventory),name='withdraw_from_others_inventory'),
]
