from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "vendor", "price", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("title", "vendor__username")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "guest_name", "status", "total_amount", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "guest_name", "guest_email", "user__username")
    inlines = [OrderItemInline]