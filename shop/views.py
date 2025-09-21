from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Shop, Product, DropshipImport, Order
from .serializers import (
    ShopSerializer,
    ProductSerializer,
    ProductCreateSerializer,
    OrderSerializer,
    OrderListSerializer,
)

User = get_user_model()

# Shops
class ShopListView(generics.ListAPIView):
    queryset = Shop.objects.prefetch_related('products', 'owner').all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_shop(request):
    try:
        shop, _ = Shop.objects.get_or_create(owner=request.user, defaults={
            'name': request.user.company_name or f"{request.user.username}'s Shop",
            'company_name': request.user.company_name or '',
            'shop_type': 'dropshipper' if request.user.role == 'dropshipper' else 'vendor',
        })
        return Response(ShopSerializer(shop, context={'request': request}).data)
    except Exception as e:
        return Response({'detail': 'Failed to retrieve shop information'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_my_shop(request):
    from django.core.files.uploadedfile import UploadedFile

    try:
        shop, _ = Shop.objects.get_or_create(owner=request.user, defaults={
            'shop_type': 'dropshipper' if request.user.role == 'dropshipper' else 'vendor',
        })
        name = request.data.get('name')
        company_name = request.data.get('company_name')

        # Accept only actual files for 'logo'; allow clearing via null/empty values
        # Support common field names: 'logo', 'image', or 'file'
        logo_file = (
            request.FILES.get('logo')
            or request.FILES.get('image')
            or request.FILES.get('file')
        )
        logo_raw = request.data.get('logo', None)

        if name is not None:
            shop.name = name
        if company_name is not None:
            shop.company_name = company_name

        if isinstance(logo_file, UploadedFile):
            shop.logo = logo_file
        elif 'logo' in request.data and (logo_raw in [None, '', 'null']):
            # Explicitly clear existing logo
            if shop.logo:
                shop.logo.delete(save=False)
            shop.logo = None
        # If 'logo' is a non-file string (e.g., URL/empty), ignore to avoid errors

        shop.save()
        return Response(ShopSerializer(shop, context={'request': request}).data)
    except Exception as e:
        return Response({'detail': 'Failed to update shop'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Products
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        vendor_id = self.request.query_params.get('vendor')
        dropshipper_id = self.request.query_params.get('dropshipper')
        
        qs = Product.objects.select_related('vendor', 'shop')
        
        if vendor_id:
            qs = qs.filter(vendor_id=vendor_id)
        elif dropshipper_id:
            # Get products imported by this dropshipper
            imported_product_ids = DropshipImport.objects.filter(
                dropshipper_id=dropshipper_id
            ).values_list('product_id', flat=True)
            qs = qs.filter(id__in=imported_product_ids)
        
        return qs.order_by('-id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        
        # If browsing by dropshipper, add dropshipper context
        dropshipper_id = self.request.query_params.get('dropshipper')
        if dropshipper_id:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                dropshipper_user = User.objects.get(id=dropshipper_id, role='dropshipper')
                context['dropshipper_user'] = dropshipper_user
            except User.DoesNotExist:
                pass
        
        return context

class MyProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        # For vendors: show products they created
        if user.role == 'vendor':
            return Product.objects.filter(vendor=user).select_related('vendor', 'shop').order_by('-id')
        
        # For dropshippers: show products they imported
        elif user.role == 'dropshipper':
            # Get products that this dropshipper has imported
            imported_product_ids = DropshipImport.objects.filter(
                dropshipper=user
            ).values_list('product_id', flat=True)
            
            return Product.objects.filter(
                id__in=imported_product_ids
            ).select_related('vendor', 'shop').order_by('-id')
        
        # Default: empty queryset for other roles
        return Product.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # If this is a dropshipper viewing their products, add dropshipper context
        if self.request.user.role == 'dropshipper':
            context['dropshipper_user'] = self.request.user
        return context

class CreateProductView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        try:
            # Attach product to the authenticated user; avoid creating Shop to prevent DB constraint issues
            # Use existing shop if present; else, proceed without a shop (Product.shop is nullable)
            shop = Shop.objects.filter(owner=self.request.user).first()
            serializer.save(vendor=self.request.user, shop=shop)
        except Exception as e:
            raise serializers.ValidationError({'detail': 'Failed to create product'})

# Dropshipper import
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def import_to_my_shop(request, pk: int):
    try:
        # Only dropshipper shops are considered for viewing in dropshipper dashboard
        # Create or get dropshipper shop for current user
        shop, _ = Shop.objects.get_or_create(owner=request.user, defaults={
            'name': request.user.company_name or f"{request.user.username}'s Shop",
            'company_name': request.user.company_name or '',
            'shop_type': 'dropshipper' if request.user.role == 'dropshipper' else 'vendor',
        })
        
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if product is already imported
        existing_import = DropshipImport.objects.filter(
            dropshipper=request.user, 
            shop=shop, 
            product=product
        ).first()
        
        if existing_import:
            return Response({'detail': 'Product already imported to your shop'}, status=status.HTTP_200_OK)
        
        # Create new import record
        DropshipImport.objects.create(dropshipper=request.user, shop=shop, product=product)
        return Response({'detail': 'Product imported to your shop successfully'}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'detail': 'Failed to import product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Orders
class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # Guest checkout allowed

class ListOrdersView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            # Vendors see orders that contain their products
            if user.role == 'vendor':
                return Order.objects.filter(items__vendor=user).distinct().order_by('-id')
            # Dropshippers see orders made via their shop
            if user.role == 'dropshipper':
                return Order.objects.filter(dropshipper_shop__owner=user).order_by('-id')
            # Fallback: empty for other roles
            return Order.objects.none()
        except Exception as e:
            return Order.objects.none()

@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_order_status(request, pk: int):
    # Only vendors can update status on orders associated with their products
    if request.user.role != 'vendor':
        return Response({'detail': 'Only vendors can update status'}, status=status.HTTP_403_FORBIDDEN)
    try:
        order = Order.objects.get(pk=pk, items__vendor=request.user)
    except Order.DoesNotExist:
        return Response({'detail': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    status_value = request.data.get('status')
    if status_value not in ['pending', 'completed']:
        return Response({'detail': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    order.status = status_value
    order.save(update_fields=['status'])
    return Response({'detail': 'Status updated'})