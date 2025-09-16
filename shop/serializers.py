from rest_framework import serializers
from django.core.files.base import ContentFile
import base64
import uuid
import imghdr

from .models import Product, Order, OrderItem
from django.contrib.auth import get_user_model

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

            # Guess file extension from header
            ext = imghdr.what(None, h=decoded_file) or "jpg"
            if ext == "jpeg":
                ext = "jpg"
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


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'guest_name', 'guest_email', 'guest_phone', 'guest_address',
            'status', 'total_amount', 'created_at', 'items'
        ]
        read_only_fields = ['user', 'status', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        order = Order.objects.create(user=user, **validated_data)
        total = 0
        for item in items_data:
            # Accept product as an ID from the frontend
            product_id = item.get('product')
            product = Product.objects.get(pk=product_id)
            quantity = item.get('quantity', 1)
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total += price * quantity
        order.total_amount = total
        order.save()
        return order