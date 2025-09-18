from django.db import models
from django.conf import settings



# Shop model
class Shop(models.Model):
    class Type(models.TextChoices):
        VENDOR = 'vendor', 'Vendor'
        DROPSHIPPER = 'dropshipper', 'Dropshipper'

    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='shops/', blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True)

    # Owner of the shop (vendor for vendor shops, dropshipper for dropshipper shops)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_shops', null=True, blank=True)
    # Backward-compatible field for existing vendor shops
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shops')

    shop_type = models.CharField(max_length=20, choices=Type.choices, default=Type.VENDOR)

    def __str__(self):
        return self.name

User = settings.AUTH_USER_MODEL

class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=0)
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        COMPLETED = 'completed', 'Completed'
        CANCELED = 'canceled', 'Canceled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # Guest checkout fields when user is None
    guest_name = models.CharField(max_length=255, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=20, blank=True)
    guest_address = models.TextField(blank=True)

    # Attribution: which dropshipper shop the order came from (if applicable)
    dropshipper_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    # Shipping/contact fields to always include for vendors/dropshippers
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot price

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {getattr(self.user, 'username', self.user_id)}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"