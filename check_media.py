import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from shop.models import Product, Shop
from django.conf import settings

print("=== PRODUCT IMAGES ===")
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
    print()

print("=== SHOP LOGOS ===")
shops = Shop.objects.all()
for shop in shops:
    print(f"Shop {shop.id}: {shop.name}")
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

print("=== MEDIA FILES ON DISK ===")
media_root = settings.MEDIA_ROOT
products_dir = os.path.join(media_root, 'products')
if os.path.exists(products_dir):
    print("Files in products directory:")
    for file in os.listdir(products_dir):
        print(f"  {file}")
else:
    print("Products directory doesn't exist")

print(f"\nMEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL: {settings.MEDIA_URL}")