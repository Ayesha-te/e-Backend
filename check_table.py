import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check if shop_order table exists
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name = 'shop_order'
""")
table_exists = cursor.fetchall()
print(f"shop_order table exists: {bool(table_exists)}")

if table_exists:
    # Get column information
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'shop_order' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("\nColumns in shop_order table:")
    for col in columns:
        print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}")
else:
    print("shop_order table does not exist")