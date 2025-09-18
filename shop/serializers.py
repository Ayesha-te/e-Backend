from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import uuid
import io
from PIL import Image
from django.contrib.auth import get_user_model

from .models import Product, Order, OrderItem, Shop

User = get_user_model()


class HybridImageField(serializers.ImageField):
    """Accept either base64 string or a standard uploaded file."""

    def to_internal_value(self, data):
        # Base64 string path
        if isinstance(data, str):
            base64_str = data
            if "data:" in data and ";base64," in data:
                try:
                    _, base64_str = data.split(";base64,", 1)
                except ValueError:
                    self.fail("invalid_image")

            try:
                decoded_file = base64.b64decode(base64_str)
            except Exception:
                self.fail("invalid_image")

            # Determine file extension using data URL header or Pillow fallback
            ext = None
            try:
                # Try to get extension from data URL header if present
                # Example: data:image/png;base64,
                if isinstance(data, str) and data.startswith('data:image/'):
                    header = data.split(';base64,', 1)[0]
                    ext = header.split('data:image/', 1)[-1]
                if not ext:
                    # Validate bytes as an image and infer format using Pillow
                    img = Image.open(io.BytesIO(decoded_file))
                    img.verify()  # verify integrity
                    img = Image.open(io.BytesIO(decoded_file))  # reopen after verify
                    fmt = (img.format or 'JPEG').upper()
                    mapping = {'JPEG': 'jpg', 'PNG': 'png', 'GIF': 'gif', 'WEBP': 'webp', 'BMP': 'bmp'}
                    ext = mapping.get(fmt, 'jpg')
                if ext == 'jpeg':
                    ext = 'jpg'
            except Exception:
                self.fail("invalid_image")

            file_name = f"{uuid.uuid4().hex[:12]}.{ext}"
            data = ContentFile(decoded_file, name=file_name)
            return super().to_internal_value(data)

        # Default behavior for uploaded files (InMemoryUploadedFile/TemporaryUploadedFile)
        return super().to_internal_value(data)


class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    name = serializers.CharField(required=False)  # Allow 'name' as input
    image_url = serializers.SerializerMethodField()  # Computed field for image URL
    image = HybridImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'name', 'description', 'price', 'image', 'image_url', 'category', 'stock', 'vendor', 'vendor_name', 'is_active', 'created_at'
        ]
        read_only_fields = ['vendor']
        extra_kwargs = {
            'title': {'required': False},
            'name': {'write_only': True},
            'image': {'required': False, 'allow_null': True},
        }

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def validate(self, data):
        # Ensure either 'title' or 'name' is provided
        if not data.get('title') and not data.get('name'):
            raise serializers.ValidationError("Either 'title' or 'name' field is required.")
        return data

    def create(self, validated_data):
        # Map 'name' to 'title' if 'title' is not provided
        if not validated_data.get('title') and validated_data.get('name'):
            validated_data['title'] = validated_data.pop('name')
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source='product.title', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_title', 'quantity', 'price']
        read_only_fields = ['price']  # price is computed from the product at creation time


class ShopSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'logo', 'logo_url', 'company_name', 'products']

    def get_logo_url(self, obj):
        request = self.context.get('request')
        # Prefer explicit shop logo
        if obj.logo:
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url
        # Fallback: use vendor's profile logo if available
        vendor_logo = getattr(getattr(obj, 'vendor', None), 'logo', None)
        if vendor_logo:
            return request.build_absolute_uri(vendor_logo.url) if request else vendor_logo.url
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'guest_name', 'guest_email', 'guest_phone', 'guest_address',
            'status', 'total_amount', 'created_at', 'items'
        ]
        read_only_fields = ['user', 'total_amount', 'status', 'created_at']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        for item in value:
            qty = item.get('quantity', 1)
            if qty is None or int(qty) < 1:
                raise serializers.ValidationError("Quantity must be at least 1 for all items.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user if 'request' in self.context else None
        order = Order.objects.create(user=user if user and user.is_authenticated else None, **validated_data)
        total = 0
        for item in items_data:
            # item['product'] will already be a Product instance thanks to PKRelatedField
            product = item['product'] if isinstance(item['product'], Product) else Product.objects.get(pk=item['product'])
            quantity = int(item.get('quantity', 1))
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total += price * quantity
        order.total_amount = total
        order.save()
        return order