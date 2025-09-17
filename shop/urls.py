from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, ShopViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'shops', ShopViewSet, basename='shop')

urlpatterns = router.urls