from django.urls import path
from .views import (
    ShopListView, my_shop, update_my_shop,
    ProductListView, MyProductsView, CreateProductView, import_to_my_shop,
    CreateOrderView, ListOrdersView, update_order_status,
)

urlpatterns = [
    # Shops
    path('shops/', ShopListView.as_view()),
    path('shops/my_shop/', my_shop),          # GET
    path('shops/my_shop/update/', update_my_shop),  # POST to update

    # Products
    path('products/', ProductListView.as_view()),
    path('products/my_products/', MyProductsView.as_view()),
    path('products/create/', CreateProductView.as_view()),
    path('products/<int:pk>/import_to_my_shop/', import_to_my_shop),

    # Orders
    path('orders/', CreateOrderView.as_view()),  # POST create guest order
    path('orders/list/', ListOrdersView.as_view()),  # GET list for vendor/dropshipper
    path('orders/<int:pk>/', update_order_status),  # PATCH vendor updates status
]