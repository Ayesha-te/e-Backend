import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check if shop_orderitem table exists and its columns
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'shop_orderitem'
    );
""")

table_exists = cursor.fetchone()[0]
print(f"shop_orderitem table exists: {table_exists}")

if table_exists:
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'shop_orderitem' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("\nColumns in shop_orderitem table:")
    for col in columns:
        print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}")
        
    # Check if there are any order items
    cursor.execute("SELECT COUNT(*) FROM shop_orderitem")
    count = cursor.fetchone()[0]
    print(f"\nExisting order items: {count}")
else:
    print("shop_orderitem table does not exist")