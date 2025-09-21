#!/usr/bin/env python3
"""
Web-based database cleanup script for Render free tier.
This script makes HTTP requests to admin endpoints to clear the database.
"""

import requests
import json
import time

BASE_URL = "https://e-backend-z33v.onrender.com"
SECRET_KEY = "CLEAR_ALL_TEST_DATA_2025"

def check_database_status():
    """Check current database status."""
    
    print("📊 Checking current database status...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/shop/admin/database-status/", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                counts = data['counts']
                print(f"   Users: {counts['users']}")
                print(f"   Shops: {counts['shops']}")
                print(f"   Products: {counts['products']}")
                print(f"   Orders: {counts['orders']}")
                print(f"   Order Items: {counts['order_items']}")
                print(f"   Dropship Imports: {counts['dropship_imports']}")
                print(f"   Total Records: {data['total_records']}")
                return data
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    return None

def clear_database():
    """Clear all data from the database."""
    
    print("\n🗑️  Starting database cleanup...")
    
    try:
        payload = {
            "secret": SECRET_KEY
        }
        
        response = requests.post(
            f"{BASE_URL}/api/shop/admin/clear-database/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print("✅ Database cleared successfully!")
                print("\n📊 Summary:")
                print("Initial counts:")
                for key, value in data['initial_counts'].items():
                    print(f"   {key}: {value}")
                print("\nDeleted counts:")
                for key, value in data['deleted_counts'].items():
                    print(f"   {key}: {value}")
                print("\nFinal counts:")
                for key, value in data['final_counts'].items():
                    print(f"   {key}: {value}")
                
                if data['fully_clean']:
                    print("\n🎉 Database is completely clean!")
                else:
                    print("\n⚠️  Some data may still remain.")
                    
                return True
            else:
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
        elif response.status_code == 403:
            print("❌ Access denied: Invalid secret key")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    return False

def main():
    print("🧹 Web-based Database Cleanup Tool")
    print("=" * 40)
    print("This tool will clear ALL data from your production database!")
    print()
    
    # Check current status
    status = check_database_status()
    
    if not status:
        print("❌ Cannot connect to the database. Please check if the backend is running.")
        return
    
    if status['total_records'] == 0:
        print("\n✅ Database is already clean!")
        return
    
    print(f"\n⚠️  Found {status['total_records']} total records in the database.")
    print("This will delete ALL users, shops, products, orders, and related data.")
    print()
    
    # Ask for confirmation
    confirmation = input("Type 'YES DELETE ALL' to confirm: ")
    
    if confirmation == "YES DELETE ALL":
        success = clear_database()
        
        if success:
            print("\n🎯 Next steps:")
            print("1. Your database is now clean")
            print("2. Deploy your frontend if needed") 
            print("3. Your app is ready for production users!")
        else:
            print("\n❌ Cleanup failed. Please try again or check the backend logs.")
    else:
        print("❌ Operation cancelled. Database was not modified.")

if __name__ == "__main__":
    main()