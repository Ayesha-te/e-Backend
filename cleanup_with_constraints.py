import requests
import json

print("🧹 Database Cleanup with Cart Handling")
print("=" * 40)
print("Handling foreign key constraints including cart data...")
print()

def clear_with_sql():
    """Try to clear using raw SQL commands."""
    
    # SQL commands to clear data in correct order
    sql_commands = [
        "DELETE FROM shop_cart WHERE 1=1;",
        "DELETE FROM shop_orderitem WHERE 1=1;", 
        "DELETE FROM shop_order WHERE 1=1;",
        "DELETE FROM shop_dropshipimport WHERE 1=1;",
        "DELETE FROM shop_product WHERE 1=1;",
        "DELETE FROM shop_shop WHERE 1=1;",
        "DELETE FROM accounts_user WHERE 1=1;"
    ]
    
    print("🔧 Alternative: Execute these SQL commands in your database:")
    print("=" * 50)
    for i, cmd in enumerate(sql_commands, 1):
        print(f"{i}. {cmd}")
    
    print("\n💡 You can run these commands in:")
    print("- Render database console (if available)")
    print("- Database admin tool")
    print("- Django shell with raw SQL")

def try_api_cleanup():
    """Try the API cleanup method."""
    try:
        print("🔄 Trying API cleanup...")
        
        payload = {"secret": "CLEAR_ALL_TEST_DATA_2025"}
        
        response = requests.post(
            "https://e-backend-z33v.onrender.com/api/shop/admin/clear-database/",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("✅ Database cleared successfully via API!")
                print(f"🗑️  Total deleted: {sum(data['deleted_counts'].values())}")
                if data["fully_clean"]:
                    print("🎉 Database is completely clean!")
                return True
            else:
                print(f"❌ API Error: {data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            if response.status_code == 500:
                error_data = response.json()
                print(f"Error details: {error_data.get('error', '')}")
                
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    return False

# Try API first, fallback to SQL instructions
if not try_api_cleanup():
    print("\n" + "="*50)
    print("📋 MANUAL CLEANUP REQUIRED")
    print("="*50)
    clear_with_sql()
    
    print("\n🎯 Quick Django Shell Method:")
    print("If you can access Django shell, run:")
    print("""
from django.db import connection
cursor = connection.cursor()
cursor.execute("DELETE FROM shop_cart WHERE 1=1")
cursor.execute("DELETE FROM shop_orderitem WHERE 1=1") 
cursor.execute("DELETE FROM shop_order WHERE 1=1")
cursor.execute("DELETE FROM shop_dropshipimport WHERE 1=1")
cursor.execute("DELETE FROM shop_product WHERE 1=1")
cursor.execute("DELETE FROM shop_shop WHERE 1=1")
cursor.execute("DELETE FROM accounts_user WHERE 1=1")
print("Database cleared!")
""")