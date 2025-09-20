from django.contrib import admin
from .models import Shop, Product, DropshipImport, Order, OrderItem

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'company_name')
    search_fields = ('name', 'company_name', 'owner__username')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'vendor', 'shop', 'price', 'stock')
    list_filter = ('vendor', 'shop')
    search_fields = ('title', 'vendor__username', 'shop__name')

@admin.register(DropshipImport)
class DropshipImportAdmin(admin.ModelAdmin):
    list_display = ('id', 'dropshipper', 'shop', 'product', 'created_at')
    list_filter = ('dropshipper', 'shop')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'created_at', 'customer_name', 'dropshipper_shop')
    list_filter = ('status',)
    inlines = [OrderItemInline]