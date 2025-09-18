from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProductViewSet, OrderViewSet, ShopViewSet, CartViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'shops', ShopViewSet, basename='shop')

cart_list = CartViewSet.as_view({'get': 'list'})
cart_add = CartViewSet.as_view({'post': 'add'})
cart_update = CartViewSet.as_view({'patch': 'update_item'})
cart_remove = CartViewSet.as_view({'delete': 'remove'})

urlpatterns = [
    *router.urls,
    path('cart/', cart_list, name='cart-list'),
    path('cart/add/', cart_add, name='cart-add'),
    path('cart/update_item/', cart_update, name='cart-update-item'),
    path('cart/remove/', cart_remove, name='cart-remove'),
]

# Additional actions:
# - /api/shop/products/{id}/import_to_my_shop/ (POST)
# - /api/shop/shops/my_shop/ (GET, POST)