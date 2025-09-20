from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Shop(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255, blank=True)
    logo = models.ImageField(upload_to='shop_logos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} (owner={self.owner})"

    @property
    def logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return None

class Product(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=0)

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
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=50)
    customer_address = models.TextField()

    shipping_phone = models.CharField(max_length=50, blank=True)
    shipping_address = models.TextField(blank=True)

    dropshipper_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    # Attribution fields for convenience in reporting
    dropshipper_shop_name = models.CharField(max_length=255, blank=True, null=True)
    dropshipper_shop_logo = models.ImageField(upload_to='order_shop_logos/', blank=True, null=True)

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