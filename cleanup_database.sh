#!/bin/bash
# Simple one-liner to clear all test data
# Run this on your Render backend console

echo "🗑️  Clearing all test data from database..."

python manage.py shell -c "
from accounts.models import User
from shop.models import Shop, Product, Order, OrderItem, DropshipImport

print('📊 Before cleanup:')
print(f'  Users: {User.objects.count()}')
print(f'  Shops: {Shop.objects.count()}')
print(f'  Products: {Product.objects.count()}')
print(f'  Orders: {Order.objects.count()}')
print(f'  Order Items: {OrderItem.objects.count()}')
print(f'  Dropship Imports: {DropshipImport.objects.count()}')

print('\\n🗑️  Deleting data...')

# Delete in correct order
OrderItem.objects.all().delete()
print('✅ Deleted order items')

Order.objects.all().delete()
print('✅ Deleted orders')

DropshipImport.objects.all().delete()
print('✅ Deleted dropship imports')

Product.objects.all().delete()
print('✅ Deleted products')

Shop.objects.all().delete()
print('✅ Deleted shops')

User.objects.all().delete()
print('✅ Deleted users')

print('\\n📊 After cleanup:')
print(f'  Users: {User.objects.count()}')
print(f'  Shops: {Shop.objects.count()}')
print(f'  Products: {Product.objects.count()}')
print(f'  Orders: {Order.objects.count()}')
print(f'  Order Items: {OrderItem.objects.count()}')
print(f'  Dropship Imports: {DropshipImport.objects.count()}')

print('\\n🎉 Database cleanup completed!')
"

echo "✅ Cleanup script completed!"