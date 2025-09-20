import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from shop.models import Order
from shop.serializers import OrderListSerializer

print("Testing Order model and serializer...")

try:
    # Test basic query
    orders = Order.objects.all()
    print(f"✓ Successfully queried {orders.count()} orders")
    
    # Test serializer
    serializer = OrderListSerializer(orders, many=True)
    data = serializer.data
    print(f"✓ Serializer works, returned {len(data)} items")
    
    if data:
        print(f"Sample order data:")
        for key, value in data[0].items():
            print(f"  {key}: {value}")
    
    print("\n✅ Order endpoints should work now!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()