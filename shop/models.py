from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Shop(models.Model):
    SHOP_TYPE_CHOICES = (
        ('vendor', 'Vendor Shop'),
        ('dropshipper', 'Dropshipper Shop'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)
    shop_type = models.CharField(max_length=20, choices=SHOP_TYPE_CHOICES, default='vendor')

    def __str__(self):
        return f"{self.name} (owner={self.owner}, type={self.shop_type})"

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return None

class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    # Align with DB: ensure non-null value during inserts
    is_active = models.BooleanField(default=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=0)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

class DropshipImport(models.Model):
    dropshipper = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imports')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='imports')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='imported_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('dropshipper', 'shop', 'product')

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    )
    # Customer fields (main customer info) - can be empty, guest fields are used instead
    customer_name = models.CharField(max_length=255, default='')
    customer_email = models.EmailField(default='')
    customer_phone = models.CharField(max_length=50, default='')
    customer_address = models.TextField(default='')

    # Guest fields (primary customer info - required in database)
    guest_name = models.CharField(max_length=255)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=50)
    guest_address = models.TextField()

    # Shipping info
    shipping_phone = models.CharField(max_length=50)
    shipping_address = models.TextField()

    # User reference (for registered customers)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    # Shop reference
    dropshipper_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    # Attribution fields for convenience in reporting
    dropshipper_shop_name = models.CharField(max_length=255, blank=True, null=True)
    dropshipper_shop_logo = models.CharField(max_length=100, blank=True, null=True)  # Using CharField to match DB

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    vendor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='order_items')

    def save(self, *args, **kwargs):
        # snapshot product title and vendor at time of ordering
        if not self.product_title:
            self.product_title = self.product.title
        if not self.price:
            self.price = self.product.price
        if not self.vendor_id:
            self.vendor = self.product.vendor
        super().save(*args, **kwargs)