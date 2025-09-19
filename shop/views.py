import logging
from rest_framework import viewsets, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Product, Order, Shop, Cart, CartItem
from .serializers import ProductSerializer, OrderSerializer, ShopSerializer, CartSerializer, CartItemSerializer
# ShopViewSet for listing shops with logo and products
class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    # Public listing should expose only dropshipper shops and their products
    queryset = Shop.objects.filter(shop_type=Shop.Type.DROPSHIPPER).prefetch_related('products')
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get', 'post'], permission_classes=[permissions.IsAuthenticated], parser_classes=[parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser])
    def my_shop(self, request):
        """Get or create the current user's dropshipper shop and allow updating name/logo/company_name."""
        user = request.user
        shop, created = Shop.objects.get_or_create(owner=user, shop_type=Shop.Type.DROPSHIPPER, defaults={
            'name': getattr(user, 'company_name', '') or f"{user.username}'s Shop",
            'company_name': getattr(user, 'company_name', '') or '',
            'vendor': user,  # keep backward-compat linkage
        })
        if request.method == 'POST':
            # Support both JSON and multipart (for logo file upload)
            name = request.data.get('name')
            company_name = request.data.get('company_name')
            logo = request.data.get('logo') or request.FILES.get('logo')
            if name is not None:
                shop.name = name
            if company_name is not None:
                shop.company_name = company_name
            if logo is not None:
                shop.logo = logo
            shop.save()
        ser = self.get_serializer(shop, context={'request': request})
        return Response(ser.data)

logger = logging.getLogger(__name__)

User = get_user_model()

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (getattr(request.user, 'role', None) in ['vendor', 'customer'] or request.user.is_superuser)
        )

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('vendor', 'shop')
    serializer_class = ProductSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsVendor()]
        elif self.action in ['my_products', 'import_to_my_shop']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            qs = qs.filter(vendor_id=vendor_id)
        # When listing, show only vendor products unless the user is a vendor
        if self.action == 'list':
            user = self.request.user
            if not user.is_authenticated or getattr(user, 'role', None) != 'vendor':
                qs = qs.filter(shop__shop_type=Shop.Type.VENDOR)
        return qs

    def perform_create(self, serializer):
        # Ensure the product is linked to the vendor and their VENDOR-type shop
        # Avoid accidentally reusing a DROPSHIPPER shop that shares the same vendor FK
        shop = Shop.objects.filter(vendor=self.request.user, shop_type=Shop.Type.VENDOR).first()
        if not shop:
            shop = Shop.objects.create(
                vendor=self.request.user,
                owner=self.request.user,
                shop_type=Shop.Type.VENDOR,
                name=getattr(self.request.user, 'company_name', None) or f"{self.request.user.username}'s Shop",
                company_name=getattr(self.request.user, 'company_name', '') or '',
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
        # Vendor: their own products; Dropshipper: products in their own shop
        user = request.user
        if getattr(user, 'role', None) == 'dropshipper':
            products = Product.objects.filter(shop__owner=user)
        else:
            products = Product.objects.filter(vendor=user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def import_to_my_shop(self, request, pk=None):
        """Dropshipper clones a vendor product into their own shop for display/sale."""
        user = request.user
        if not user.is_authenticated or getattr(user, 'role', None) != 'dropshipper':
            return Response({'detail': 'Dropshipper only'}, status=403)
        try:
            src: Product = self.get_object()
        except Product.DoesNotExist:
            return Response({'detail': 'Not found'}, status=404)

        # Find or create dropshipper default shop
        shop, _ = Shop.objects.get_or_create(owner=user, shop_type=Shop.Type.DROPSHIPPER, defaults={
            'name': getattr(user, 'company_name', '') or f"{user.username}'s Shop",
            'company_name': getattr(user, 'company_name', '') or '',
            'vendor': user,
        })

        # Create a new product under dropshipper shop, keeping vendor attribution to original src.vendor
        clone = Product.objects.create(
            title=src.title,
            description=src.description,
            price=src.price,
            image=src.image,
            category=src.category,
            stock=src.stock,
            vendor=src.vendor,  # vendor remains original vendor
            shop=shop,
            is_active=True,
        )
        return Response(ProductSerializer(clone, context={'request': request}).data, status=201)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related('items__product', 'dropshipper_shop')
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
            # Vendor sees orders containing their products
            return Order.objects.filter(items__product__vendor=user).distinct()
        if getattr(user, 'role', None) == 'dropshipper':
            # Dropshipper sees orders assigned to their shop
            return Order.objects.filter(dropshipper_shop__owner=user).distinct()
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Order create validation errors: %s", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_or_create_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    def list(self, request):
        cart = self._get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self._get_or_create_cart(request.user)
        product_id = request.data.get('product')
        quantity = max(1, int(request.data.get('quantity', 1)))
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Invalid product'}, status=400)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        cart = self._get_or_create_cart(request.user)
        item_id = request.data.get('id')
        quantity = int(request.data.get('quantity', 1))
        try:
            item = cart.items.get(pk=item_id)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=404)
        if quantity < 1:
            item.delete()
        else:
            item.quantity = quantity
            item.save()
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['delete'])
    def remove(self, request):
        cart = self._get_or_create_cart(request.user)
        item_id = request.data.get('id')
        try:
            item = cart.items.get(pk=item_id)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=404)
        return Response(CartSerializer(cart).data)