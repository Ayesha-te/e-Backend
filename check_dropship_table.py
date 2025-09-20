import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Check if shop_dropshipimport table exists
cursor.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'shop_dropshipimport'
    );
""")

table_exists = cursor.fetchone()[0]
print(f"shop_dropshipimport table exists: {table_exists}")

if not table_exists:
    print("Creating shop_dropshipimport table...")
    
    # Create the table manually
    cursor.execute("""
        CREATE TABLE shop_dropshipimport (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            dropshipper_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES shop_product(id) ON DELETE CASCADE,
            shop_id INTEGER NOT NULL REFERENCES shop_shop(id) ON DELETE CASCADE,
            UNIQUE(dropshipper_id, shop_id, product_id)
        );
    """)
    
    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX shop_dropshipimport_dropshipper_id_idx ON shop_dropshipimport(dropshipper_id);
        CREATE INDEX shop_dropshipimport_product_id_idx ON shop_dropshipimport(product_id);
        CREATE INDEX shop_dropshipimport_shop_id_idx ON shop_dropshipimport(shop_id);
    """)
    
    print("✅ Created shop_dropshipimport table successfully")
else:
    print("Table already exists")
    
    # Show current structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'shop_dropshipimport' 
        ORDER BY ordinal_position
    """)
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(f"  {col[0]} ({col[1]}) - nullable: {col[2]}")