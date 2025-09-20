import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check nullable constraints and defaults for missing columns
cursor.execute("""
    SELECT column_name, is_nullable, column_default, data_type
    FROM information_schema.columns 
    WHERE table_name = 'shop_order' 
    AND column_name IN ('guest_name', 'guest_email', 'guest_phone', 'guest_address', 'total_amount', 'user_id')
    ORDER BY column_name
""")

columns_info = cursor.fetchall()
print("Database column constraints for missing fields:")
for col_name, nullable, default, data_type in columns_info:
    print(f"  {col_name}: {data_type}, nullable={nullable}, default={default}")

# Check if there are any existing orders
cursor.execute("SELECT COUNT(*) FROM shop_order")
order_count = cursor.fetchone()[0]
print(f"\nExisting orders in database: {order_count}")

# If there are existing orders, show a sample to understand the data
if order_count > 0:
    cursor.execute("SELECT id, customer_name, guest_name, total_amount FROM shop_order LIMIT 3")
    orders = cursor.fetchall()
    print("\nSample orders:")
    for order in orders:
        print(f"  ID {order[0]}: customer={order[1]}, guest={order[2]}, total={order[3]}")