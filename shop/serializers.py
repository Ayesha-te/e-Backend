from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Shop, Product, DropshipImport, Order, OrderItem

User = get_user_model()

class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'company_name']

class ShopSerializer(serializers.ModelSerializer):
    owner = UserMiniSerializer(read_only=True)
    logo_url = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ['id', 'name', 'company_name', 'logo_url', 'owner', 'products']

    def get_products(self, obj):
        # Expose vendor products attached to this shop
        from .models import Product
        prods = obj.products.all().select_related('vendor', 'shop')
        return ProductSerializer(prods, many=True, context=self.context).data

    def get_logo_url(self, obj):
        request = self.context.get('request')
        if obj.logo and hasattr(obj.logo, 'url'):
            url = obj.logo.url
            return request.build_absolute_uri(url) if request else url
        return None

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)
    shop_name = serializers.CharField(source='shop.name', read_only=True)
    shop_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'image_url', 'category', 'stock', 'vendor_name', 'shop_name', 'shop_logo_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_shop_logo_url(self, obj):
        request = self.context.get('request')
        if obj.shop and obj.shop.logo and hasattr(obj.shop.logo, 'url'):
            url = obj.shop.logo.url
            return request.build_absolute_uri(url) if request else url
        return None

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'image', 'category', 'stock']

class DropshipImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropshipImport
        fields = ['id', 'dropshipper', 'shop', 'product', 'created_at']
        read_only_fields = ['dropshipper', 'shop', 'created_at']

class OrderItemInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemInputSerializer(many=True)
    total_amount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'shipping_phone', 'shipping_address', 'dropshipper_shop', 'items', 'status', 'created_at',
            'dropshipper_shop_name'
        ]
        read_only_fields = ['status', 'created_at']

    def get_total_amount(self, obj):
        return sum([float(i.price) * i.quantity for i in obj.items.all()])

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        dropshipper_shop = validated_data.get('dropshipper_shop')
        if dropshipper_shop:
            validated_data['dropshipper_shop_name'] = dropshipper_shop.name
        order = Order.objects.create(**validated_data)
        for item in items_data:
            product = item['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_title=product.title,
                quantity=item['quantity'],
                price=product.price,
                vendor=product.vendor,
            )
        return order

class OrderListSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'created_at',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'dropshipper_shop', 'dropshipper_shop_name', 'items'
        ]

    def get_items(self, obj):
        return [
            {
                'id': i.id,
                'product': i.product_id,
                'product_title': i.product_title,
                'quantity': i.quantity,
                'price': str(i.price),
            }
            for i in obj.items.all()
        ]

    def get_total_amount(self, obj):
        return str(sum([i.price * i.quantity for i in obj.items.all()]))