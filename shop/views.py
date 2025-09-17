import logging
from rest_framework import viewsets, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Product, Order, Shop
from .serializers import ProductSerializer, OrderSerializer, ShopSerializer
# ShopViewSet for listing shops with logo and products
class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Shop.objects.all().prefetch_related('products')
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]

logger = logging.getLogger(__name__)

User = get_user_model()

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'vendor'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('vendor')
    serializer_class = ProductSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_products']:
            return [permissions.IsAuthenticated(), IsVendor()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            qs = qs.filter(vendor_id=vendor_id)
        return qs

    def perform_create(self, serializer):
        # Ensure the product is linked to the vendor and their default shop
        # Create/get a default shop for this user if not exists
        shop, _ = Shop.objects.get_or_create(
            vendor=self.request.user,
            defaults={
                'name': getattr(self.request.user, 'company_name', None) or f"{self.request.user.username}'s Shop",
                'company_name': getattr(self.request.user, 'company_name', '') or '',
            },
        )
        serializer.save(vendor=self.request.user, shop=shop)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # Use safe, parameterized logging to avoid heavy string building
            logger.warning("Serializer errors: %s", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @action(detail=False, methods=['get'])
    def my_products(self, request):
        products = Product.objects.filter(vendor=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Order.objects.none()
        if getattr(user, 'role', None) == 'vendor':
            # Show orders that include vendor's products
            return Order.objects.filter(items__product__vendor=user).distinct()
        if getattr(user, 'role', None) == 'dropshipper':
            # Placeholder: show all for dropshipper or apply logic later
            return Order.objects.all()
        return Order.objects.filter(user=user)