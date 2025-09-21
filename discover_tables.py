import requests
import json

print("🔍 Database Table Discovery")
print("=" * 40)
print("Let's find out what tables actually exist in your database!")
print()

print("🐚 Run this in your Django shell to discover table names:")
print("python manage.py shell")
print()
print("Then copy and paste these commands:")
print("-" * 40)

discovery_commands = '''
from django.db import connection

# Get all table names
cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("📋 All tables in your database:")
for table in tables:
    print(f"   - {table[0]}")

print("\\n🔍 Looking for shop/user related tables:")
shop_tables = [t[0] for t in tables if 'shop' in t[0].lower() or 'user' in t[0].lower() or 'account' in t[0].lower()]
for table in shop_tables:
    print(f"   ✅ {table}")

print("\\n🔍 Checking table record counts:")
from accounts.models import User
from shop.models import Shop, Product

try:
    print(f"Users: {User.objects.count()}")
except Exception as e:
    print(f"Users table error: {e}")

try:
    print(f"Shops: {Shop.objects.count()}")
except Exception as e:
    print(f"Shops table error: {e}")

try:
    print(f"Products: {Product.objects.count()}")
except Exception as e:
    print(f"Products table error: {e}")

print("\\n📝 Django model table names:")
print(f"User model uses table: {User._meta.db_table}")
print(f"Shop model uses table: {Shop._meta.db_table}")
print(f"Product model uses table: {Product._meta.db_table}")

from shop.models import Order, OrderItem, DropshipImport
try:
    print(f"Order model uses table: {Order._meta.db_table}")
    print(f"OrderItem model uses table: {OrderItem._meta.db_table}")
    print(f"DropshipImport model uses table: {DropshipImport._meta.db_table}")
except Exception as e:
    print(f"Model table error: {e}")
'''

print(discovery_commands)
print("-" * 40)

print("\n💡 This will show us:")
print("1. All actual table names in your database")
print("2. Which tables have data")
print("3. The correct table names to use for cleanup")
print("\nRun this first, then we'll create the correct cleanup commands!")