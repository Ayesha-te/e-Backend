import requests
import json

print("🧹 Database Cleanup - Simple Version")
print("=" * 40)

def simple_shell_cleanup():
    """Provide shell commands without the problematic cart table."""
    
    print("🐚 Run this in your Django shell:")
    print("python manage.py shell")
    print()
    print("Then copy and paste these commands:")
    print("-" * 40)
    
    shell_commands = '''
from django.db import connection
from accounts.models import User
from shop.models import Shop, Product, Order, OrderItem, DropshipImport

# Get initial counts
print("📊 Before cleanup:")
print(f"Users: {User.objects.count()}")
print(f"Shops: {Shop.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"Order Items: {OrderItem.objects.count()}")
print(f"Dropship Imports: {DropshipImport.objects.count()}")

# Clear data using raw SQL (skip cart table since it doesn't exist)
cursor = connection.cursor()

print("\\n🗑️ Deleting data...")

# Delete in correct order to handle foreign keys
cursor.execute("DELETE FROM shop_orderitem WHERE 1=1") 
print("✅ Deleted order items")

cursor.execute("DELETE FROM shop_order WHERE 1=1")
print("✅ Deleted orders")

cursor.execute("DELETE FROM shop_dropshipimport WHERE 1=1")
print("✅ Deleted dropship imports")

cursor.execute("DELETE FROM shop_product WHERE 1=1")
print("✅ Deleted products")

cursor.execute("DELETE FROM shop_shop WHERE 1=1")
print("✅ Deleted shops")

cursor.execute("DELETE FROM accounts_user WHERE 1=1")
print("✅ Deleted users")

# Verify cleanup
print("\\n📊 After cleanup:")
print(f"Users: {User.objects.count()}")
print(f"Shops: {Shop.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
print(f"Order Items: {OrderItem.objects.count()}")
print(f"Dropship Imports: {DropshipImport.objects.count()}")

print("\\n🎉 Database cleanup completed!")
'''
    
    print(shell_commands)
    print("-" * 40)

def one_liner_cleanup():
    """Provide one-liner command without cart table."""
    
    print("\n🚀 Or use this one-liner command:")
    print("-" * 40)
    
    one_liner = '''python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('DELETE FROM shop_orderitem WHERE 1=1') 
cursor.execute('DELETE FROM shop_order WHERE 1=1')
cursor.execute('DELETE FROM shop_dropshipimport WHERE 1=1')
cursor.execute('DELETE FROM shop_product WHERE 1=1')
cursor.execute('DELETE FROM shop_shop WHERE 1=1')
cursor.execute('DELETE FROM accounts_user WHERE 1=1')
print('✅ Database cleared successfully!')
"'''
    
    print(one_liner)

# Show both options
simple_shell_cleanup()
one_liner_cleanup()

print("\n💡 The shop_cart table doesn't exist, so we skip it.")
print("This should work without any errors!")