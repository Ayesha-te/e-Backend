from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'image_url', 'category', 'vendor', 'vendor_name', 'is_active', 'created_at'
        ]
        read_only_fields = ['vendor']

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