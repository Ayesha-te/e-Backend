import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from shop.models import Order

try:
    # Test basic query
    orders = Order.objects.all()
    print(f"Successfully queried {orders.count()} orders")
    
    # Test accessing fields
    for order in orders[:2]:
        print(f"Order {order.id}:")
        print(f"  Guest: {order.guest_name} ({order.guest_email})")
        print(f"  Customer: {order.customer_name} ({order.customer_email})")
        print(f"  Total: ${order.total_amount}")
        print(f"  Status: {order.status}")
        print()
        
    print("✓ Order model is working correctly with the database!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()