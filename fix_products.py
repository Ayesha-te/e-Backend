#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop.models import Product, Shop
from accounts.models import User

def fix_products():
    # Get all products without shops
    products_without_shops = Product.objects.filter(shop__isnull=True)
    print(f'Found {products_without_shops.count()} products without shops')

    for product in products_without_shops:
        vendor = product.vendor
        # Find or create vendor shop
        shop = Shop.objects.filter(vendor=vendor, shop_type=Shop.Type.VENDOR).first()
        if not shop:
            shop = Shop.objects.create(
                vendor=vendor,
                owner=vendor,
                shop_type=Shop.Type.VENDOR,
                name=getattr(vendor, 'company_name', None) or f"{vendor.username}'s Shop",
                company_name=getattr(vendor, 'company_name', '') or '',
            )
            print(f'Created shop: {shop.name} for vendor: {vendor.username}')

        # Link product to shop
        product.shop = shop
        product.save()
        print(f'Linked product {product.title} to shop {shop.name}')

    print('Done fixing products')

if __name__ == '__main__':
    fix_products()