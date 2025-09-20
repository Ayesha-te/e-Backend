import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

print("Adding missing columns to shop_orderitem table...")

try:
    # Add product_title column
    cursor.execute("""
        ALTER TABLE shop_orderitem 
        ADD COLUMN product_title VARCHAR(255) NOT NULL DEFAULT '';
    """)
    print("✓ Added product_title column")
except Exception as e:
    print(f"product_title column: {e}")

try:
    # Add vendor_id column  
    cursor.execute("""
        ALTER TABLE shop_orderitem 
        ADD COLUMN vendor_id INTEGER;
    """)
    print("✓ Added vendor_id column")
except Exception as e:
    print(f"vendor_id column: {e}")

# Update existing records with proper data
try:
    cursor.execute("""
        UPDATE shop_orderitem 
        SET 
            product_title = COALESCE(shop_product.title, 'Unknown Product'),
            vendor_id = COALESCE(shop_product.vendor_id, 1)
        FROM shop_product 
        WHERE shop_orderitem.product_id = shop_product.id
    """)
    print("✓ Updated existing order items with product data")
except Exception as e:
    print(f"Update error: {e}")

# Add foreign key constraint for vendor_id
try:
    cursor.execute("""
        ALTER TABLE shop_orderitem 
        ADD CONSTRAINT shop_orderitem_vendor_id_fkey 
        FOREIGN KEY (vendor_id) REFERENCES accounts_user(id) ON DELETE RESTRICT;
    """)
    print("✓ Added foreign key constraint for vendor_id")
except Exception as e:
    print(f"Foreign key constraint: {e}")

print("\nVerifying table structure...")
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'shop_orderitem' 
    ORDER BY ordinal_position
""")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}")

print("\n✅ OrderItem table should be fixed now!")