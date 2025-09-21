#!/usr/bin/env python
"""
Remote database cleanup script for production backend.
This script makes API calls to clear data without needing local Django setup.
"""

import requests
import json
import time

BASE_URL = "https://e-backend-z33v.onrender.com"

def create_admin_user_and_get_token():
    """Create a temporary admin user to perform cleanup operations."""
    
    print("🔐 Creating temporary admin user for cleanup...")
    
    # First, try to create an admin user
    admin_data = {
        "username": "temp_admin_cleanup",
        "email": "admin@cleanup.temp",
        "password": "TempCleanup123!",
        "role": "vendor",  # Use vendor role to have permissions
        "company_name": "Cleanup Admin"
    }
    
    try:
        # Create user
        response = requests.post(f"{BASE_URL}/api/accounts/signup/", 
                                headers={"Content-Type": "application/json"},
                                data=json.dumps(admin_data), 
                                timeout=30)
        
        if response.status_code in [200, 201]:
            print("✅ Temporary admin user created")
        else:
            print(f"⚠️  Admin user creation returned status {response.status_code}")
        
        # Login to get token
        login_data = {
            "username": "temp_admin_cleanup",
            "password": "TempCleanup123!"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/token/", 
                                headers={"Content-Type": "application/json"},
                                data=json.dumps(login_data), 
                                timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None

def check_database_status():
    """Check current database status."""
    
    print("\n📊 Checking current database status...")
    
    try:
        # Check products
        response = requests.get(f"{BASE_URL}/api/shop/products/", timeout=30)
        if response.status_code == 200:
            products = response.json()
            print(f"   Products: {len(products)}")
        
        # Check shops
        response = requests.get(f"{BASE_URL}/api/shop/shops/", timeout=30)
        if response.status_code == 200:
            shops = response.json()
            print(f"   Shops: {len(shops)}")
            
    except Exception as e:
        print(f"❌ Error checking database status: {e}")

def manual_cleanup_instructions():
    """Provide instructions for manual cleanup via Django admin."""
    
    print("\n🔧 Manual Cleanup Instructions:")
    print("="*50)
    print("Since we need direct database access for complete cleanup,")
    print("please follow these steps:")
    print()
    print("1. Access your Render backend dashboard")
    print("2. Open a shell/console for your backend service")
    print("3. Run the following Django management commands:")
    print()
    print("   # Delete all data in correct order")
    print("   python manage.py shell -c \"")
    print("   from shop.models import *")
    print("   from accounts.models import *")
    print("   OrderItem.objects.all().delete()")
    print("   Order.objects.all().delete()")
    print("   DropshipImport.objects.all().delete()")
    print("   Product.objects.all().delete()")
    print("   Shop.objects.all().delete()")
    print("   User.objects.all().delete()")
    print("   print('Database cleared!')\"")
    print()
    print("4. Alternatively, copy the clear_test_data.py script to your")
    print("   Render backend and run it there directly.")

if __name__ == "__main__":
    print("🧹 Remote Database Cleanup Tool")
    print("="*40)
    
    # Check current status
    check_database_status()
    
    # Since we can't directly delete all data via API (no delete endpoints),
    # provide manual instructions
    manual_cleanup_instructions()
    
    print("\n💡 Alternative: Use the local script")
    print("   If you have access to the production database locally,")
    print("   run: python clear_test_data.py")