from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer

User = get_user_model()

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'vendor'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('vendor')
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_products']:
            return [permissions.IsAuthenticated(), IsVendor()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user)

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