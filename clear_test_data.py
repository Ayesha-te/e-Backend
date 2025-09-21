#!/usr/bin/env python
"""
Script to clear all test data from the database.
This will remove all users, shops, products, orders, and related data.
Use this to prepare the database for production use.
"""

import os
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from accounts.models import User
from shop.models import Shop, Product, Order, OrderItem, DropshipImport

def clear_all_data():
    """Clear all test data from the database."""
    
    print("🗑️  Starting database cleanup...")
    
    # Clear orders and order items first (due to foreign key constraints)
    order_items_count = OrderItem.objects.count()
    orders_count = Order.objects.count()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    print(f"✅ Deleted {order_items_count} order items and {orders_count} orders")
    
    # Clear dropship imports
    dropship_imports_count = DropshipImport.objects.count()
    DropshipImport.objects.all().delete()
    print(f"✅ Deleted {dropship_imports_count} dropship imports")
    
    # Clear products
    products_count = Product.objects.count()
    Product.objects.all().delete()
    print(f"✅ Deleted {products_count} products")
    
    # Clear shops
    shops_count = Shop.objects.count()
    Shop.objects.all().delete()
    print(f"✅ Deleted {shops_count} shops")
    
    # Clear users (this will cascade to related shops if any remain)
    users_count = User.objects.count()
    User.objects.all().delete()
    print(f"✅ Deleted {users_count} users")
    
    print("\n🎉 Database cleanup completed successfully!")
    print("📊 Final counts:")
    print(f"   Users: {User.objects.count()}")
    print(f"   Shops: {Shop.objects.count()}")
    print(f"   Products: {Product.objects.count()}")
    print(f"   Orders: {Order.objects.count()}")
    print(f"   Order Items: {OrderItem.objects.count()}")
    print(f"   Dropship Imports: {DropshipImport.objects.count()}")

def test_api_endpoints():
    """Test that the API endpoints are working after cleanup."""
    
    print("\n🧪 Testing API endpoints...")
    
    base_url = "https://e-backend-z33v.onrender.com"
    
    # Test products endpoint
    try:
        response = requests.get(f"{base_url}/api/shop/products/", timeout=30)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Products API working - returned {len(products)} products")
        else:
            print(f"⚠️  Products API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Products API error: {e}")
    
    # Test shops endpoint
    try:
        response = requests.get(f"{base_url}/api/shop/shops/", timeout=30)
        if response.status_code == 200:
            shops = response.json()
            print(f"✅ Shops API working - returned {len(shops)} shops")
        else:
            print(f"⚠️  Shops API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Shops API error: {e}")

if __name__ == "__main__":
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print("This includes all users, shops, products, orders, and related data.")
    print()
    
    # For safety, require explicit confirmation
    confirmation = input("Type 'DELETE ALL DATA' to confirm: ")
    
    if confirmation == "DELETE ALL DATA":
        clear_all_data()
        test_api_endpoints()
    else:
        print("❌ Operation cancelled. Database was not modified.")
        print("To proceed, run the script again and type 'DELETE ALL DATA' exactly.")