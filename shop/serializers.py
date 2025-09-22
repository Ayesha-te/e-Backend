from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Shop, Product, ProductImage, DropshipImport, Order, OrderItem

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
            # Check if file actually exists
            try:
                if obj.logo.storage.exists(obj.logo.name):
                    url = obj.logo.url
                    return request.build_absolute_uri(url) if request else url
            except:
                pass
        return None

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'is_primary', 'order']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            try:
                if obj.image.storage.exists(obj.image.name):
                    url = obj.image.url
                    return request.build_absolute_uri(url) if request else url
            except:
                pass
        return None

class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    images = ProductImageSerializer(source='product_images', many=True, read_only=True)
    all_images = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    shop_logo_url = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'image_url', 'images', 'all_images', 'category', 'stock', 'is_active', 'shop_name', 'shop_logo_url', 'vendor_name']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            # Check if file actually exists
            try:
                if obj.image.storage.exists(obj.image.name):
                    url = obj.image.url
                    return request.build_absolute_uri(url) if request else url
            except:
                pass
        return None

    def get_shop_name(self, obj):
        # Check if we have a dropshipper context for this product
        dropshipper_user = self.context.get('dropshipper_user')
        if dropshipper_user:
            # Try to get the dropshipper's shop
            try:
                dropshipper_shop = Shop.objects.filter(owner=dropshipper_user, shop_type='dropshipper').first()
                if dropshipper_shop:
                    return dropshipper_shop.name
            except:
                pass
        
        # Fallback to original vendor shop
        return obj.shop.name if obj.shop else None

    def get_shop_logo_url(self, obj):
        request = self.context.get('request')
        
        # Check if we have a dropshipper context for this product
        dropshipper_user = self.context.get('dropshipper_user')
        if dropshipper_user:
            # Try to get the dropshipper's shop logo
            try:
                dropshipper_shop = Shop.objects.filter(owner=dropshipper_user, shop_type='dropshipper').first()
                if dropshipper_shop and dropshipper_shop.logo and hasattr(dropshipper_shop.logo, 'url'):
                    if dropshipper_shop.logo.storage.exists(dropshipper_shop.logo.name):
                        url = dropshipper_shop.logo.url
                        return request.build_absolute_uri(url) if request else url
            except:
                pass
        
        # Fallback to original vendor shop logo
        if obj.shop and obj.shop.logo and hasattr(obj.shop.logo, 'url'):
            # Check if file actually exists
            try:
                if obj.shop.logo.storage.exists(obj.shop.logo.name):
                    url = obj.shop.logo.url
                    return request.build_absolute_uri(url) if request else url
            except:
                pass
        return None

    def get_vendor_name(self, obj):
        if obj.vendor:
            return obj.vendor.company_name or obj.vendor.username
        return None

    def get_all_images(self, obj):
        """Get all images for this product including the main image"""
        request = self.context.get('request')
        images = []
        
        # Add main image if exists
        if obj.image and hasattr(obj.image, 'url'):
            try:
                if obj.image.storage.exists(obj.image.name):
                    url = obj.image.url
                    images.append({
                        'id': 'main',
                        'image_url': request.build_absolute_uri(url) if request else url,
                        'is_primary': True,
                        'order': 0
                    })
            except:
                pass
        
        # Add additional images
        for idx, img in enumerate(obj.product_images.all(), start=1):
            if img.image and hasattr(img.image, 'url'):
                try:
                    if img.image.storage.exists(img.image.name):
                        url = img.image.url
                        images.append({
                            'id': img.id,
                            'image_url': request.build_absolute_uri(url) if request else url,
                            'is_primary': img.is_primary,
                            'order': img.order or idx
                        })
                except:
                    pass
        
        return sorted(images, key=lambda x: x['order'])

class ProductCreateSerializer(serializers.ModelSerializer):
    # Allow product creation without an image; accept 'file' alias as well
    image = serializers.ImageField(required=False, allow_null=True)
    additional_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'image', 'additional_images', 'category', 'stock', 'is_active']

    def to_internal_value(self, data):
        # If client sent 'file' instead of 'image', map it
        if 'image' not in data and 'file' in data:
            mutable_data = data.copy()
            mutable_data['image'] = mutable_data.get('file')
            data = mutable_data
        return super().to_internal_value(data)

    def create(self, validated_data):
        additional_images = validated_data.pop('additional_images', [])
        product = super().create(validated_data)
        
        # Create additional product images
        for idx, image in enumerate(additional_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                order=idx + 1,
                is_primary=False
            )
        
        return product

    def update(self, instance, validated_data):
        additional_images = validated_data.pop('additional_images', None)
        product = super().update(instance, validated_data)
        
        # Handle additional images if provided
        if additional_images is not None:
            # Remove existing additional images
            instance.product_images.all().delete()
            
            # Create new additional images
            for idx, image in enumerate(additional_images):
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    order=idx + 1,
                    is_primary=False
                )
        
        return product

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
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    # Make guest fields optional in the serializer since we'll handle them in validation
    guest_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    guest_email = serializers.EmailField(required=False, allow_blank=True)
    guest_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    guest_address = serializers.CharField(required=False, allow_blank=True)
    shipping_phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'guest_name', 'guest_email', 'guest_phone', 'guest_address',
            'shipping_phone', 'shipping_address', 'dropshipper_shop', 'items', 'status', 'created_at',
            'dropshipper_shop_name', 'total_amount', 'user'
        ]
        read_only_fields = ['status', 'created_at', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Calculate total amount from items
        total = sum([item['product'].price * item['quantity'] for item in items_data])
        validated_data['total_amount'] = total
        
        # Auto-detect dropshipper shop if not explicitly set
        if not validated_data.get('dropshipper_shop'):
            # Check if any of the products being ordered have been imported by dropshippers
            product_ids = [item['product'].id for item in items_data]
            dropship_imports = DropshipImport.objects.filter(product_id__in=product_ids).select_related('shop')
            
            if dropship_imports.exists():
                # If there are imports, use the first dropshipper shop found
                # In a real system, you'd want the frontend to specify which dropshipper context
                first_import = dropship_imports.first()
                validated_data['dropshipper_shop'] = first_import.shop
        
        # Set guest fields from customer fields if guest fields are empty
        if not validated_data.get('guest_name'):
            validated_data['guest_name'] = validated_data.get('customer_name', '')
        if not validated_data.get('guest_email'):
            validated_data['guest_email'] = validated_data.get('customer_email', '')
        if not validated_data.get('guest_phone'):
            validated_data['guest_phone'] = validated_data.get('customer_phone', '')
        if not validated_data.get('guest_address'):
            validated_data['guest_address'] = validated_data.get('customer_address', '')
        
        # Ensure required guest fields have values (database constraints)
        if not validated_data.get('guest_name'):
            validated_data['guest_name'] = 'Guest Customer'
        if not validated_data.get('guest_email'):
            validated_data['guest_email'] = 'guest@example.com'
        if not validated_data.get('guest_phone'):
            validated_data['guest_phone'] = 'N/A'
        if not validated_data.get('guest_address'):
            validated_data['guest_address'] = 'N/A'
        if not validated_data.get('shipping_phone'):
            validated_data['shipping_phone'] = validated_data.get('guest_phone', 'N/A')
        if not validated_data.get('shipping_address'):
            validated_data['shipping_address'] = validated_data.get('guest_address', 'N/A')
        
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

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total_amount', 'created_at',
            'customer_name', 'customer_email', 'customer_phone', 'customer_address',
            'guest_name', 'guest_email', 'guest_phone', 'guest_address',
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