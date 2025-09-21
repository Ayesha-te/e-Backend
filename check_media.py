import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from shop.models import Product, Shop, DropshipImport, Order, OrderItem
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

print("=== DROPSHIP IMPORTS ===")
imports = DropshipImport.objects.all().select_related('dropshipper', 'shop', 'product')
print(f"Total imports: {imports.count()}")
for imp in imports:
    print(f"Import {imp.id}: User {imp.dropshipper.username} imported product '{imp.product.title}' to shop '{imp.shop.name}'")

print("\n=== PRODUCT IMAGES ===")
products = Product.objects.all()
for product in products:
    print(f"Product {product.id}: {product.title}")
    if product.image:
        image_path = product.image.name
        full_path = os.path.join(settings.MEDIA_ROOT, image_path)
        exists = os.path.exists(full_path)
        print(f"  Image: {image_path} (exists: {exists})")
        if product.image.url:
            print(f"  URL: {product.image.url}")
    else:
        print("  No image")
    
    # Check if this product has been imported by any dropshipper
    imports_for_product = DropshipImport.objects.filter(product=product).select_related('dropshipper', 'shop')
    if imports_for_product.exists():
        print(f"  Imported by:")
        for imp in imports_for_product:
            print(f"    - {imp.dropshipper.username} to shop '{imp.shop.name}'")
    print()

print("=== SHOP LOGOS ===")
shops = Shop.objects.all()
for shop in shops:
    print(f"Shop {shop.id}: {shop.name} (Owner: {shop.owner.username})")
    if shop.logo:
        logo_path = shop.logo.name
        full_path = os.path.join(settings.MEDIA_ROOT, logo_path)
        exists = os.path.exists(full_path)
        print(f"  Logo: {logo_path} (exists: {exists})")
        if shop.logo.url:
            print(f"  URL: {shop.logo.url}")
    else:
        print("  No logo")
    print()

print("=== ORDERS ===")
orders = Order.objects.all().select_related('dropshipper_shop')
print(f"Total orders: {orders.count()}")
for order in orders:
    print(f"Order {order.id}: {order.guest_name} - {order.status}")
    if order.dropshipper_shop:
        print(f"  Dropshipper shop: {order.dropshipper_shop.name}")
    else:
        print("  No dropshipper shop")
    items = OrderItem.objects.filter(order=order).select_related('product', 'vendor')
    for item in items:
        print(f"  - {item.quantity}x {item.product_title} (vendor: {item.vendor.username})")

print("\n=== SHOP LOGOS ON DISK ===")
shop_logos_dir = os.path.join(settings.MEDIA_ROOT, 'shop_logos')
if os.path.exists(shop_logos_dir):
    print("Files in shop_logos directory:")
    for file in os.listdir(shop_logos_dir):
        print(f"  {file}")
else:
    print("Shop logos directory doesn't exist")

print("=== MEDIA FILES ON DISK ===")
products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
if os.path.exists(products_dir):
    print("Files in products directory:")
    for file in os.listdir(products_dir):
        print(f"  {file}")
else:
    print("Products directory doesn't exist")

print(f"\nMEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")