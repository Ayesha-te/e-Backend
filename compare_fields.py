import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.db import connection
from shop.models import Order

# Get model fields
model_fields = [field.name for field in Order._meta.get_fields()]
print("Django model fields:")
for field in sorted(model_fields):
    print(f"  {field}")

print("\nDatabase table columns:")
cursor = connection.cursor()
cursor.execute("""
    SELECT column_name
    FROM information_schema.columns 
    WHERE table_name = 'shop_order' 
    ORDER BY column_name
""")
db_columns = [row[0] for row in cursor.fetchall()]
for col in sorted(db_columns):
    print(f"  {col}")

print("\nFields in model but not in database:")
missing_in_db = set(model_fields) - set(db_columns)
for field in sorted(missing_in_db):
    print(f"  {field}")

print("\nColumns in database but not in model:")
missing_in_model = set(db_columns) - set(model_fields)
for col in sorted(missing_in_model):
    print(f"  {col}")