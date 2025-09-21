from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accounts.models import User
from shop.models import Shop, Product, Order, OrderItem, DropshipImport
import json


@csrf_exempt
@require_http_methods(["POST"])
def clear_database_admin(request):
    """
    Admin endpoint to clear all test data from the database.
    Requires a secret key for security.
    
    POST /api/admin/clear-database/
    Body: {"secret": "CLEAR_ALL_TEST_DATA_2025"}
    """
    
    try:
        # Parse request body
        if hasattr(request, 'body'):
            body = json.loads(request.body.decode('utf-8'))
        else:
            return JsonResponse({'error': 'Invalid request body'}, status=400)
        
        # Check secret key for security
        secret = body.get('secret')
        if secret != 'CLEAR_ALL_TEST_DATA_2025':
            return JsonResponse({'error': 'Invalid secret key'}, status=403)
        
        # Get initial counts
        initial_counts = {
            'users': User.objects.count(),
            'shops': Shop.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'order_items': OrderItem.objects.count(),
            'dropship_imports': DropshipImport.objects.count(),
        }
        
        # Clear data in correct order (respecting foreign key constraints)
        deleted_counts = {}
        
        # Clear any cart data first (if exists) using raw SQL
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM shop_cart WHERE 1=1")
                deleted_counts['carts'] = cursor.rowcount
        except Exception:
            deleted_counts['carts'] = 0  # Table might not exist
        
        # 1. Clear order items first
        deleted_counts['order_items'] = OrderItem.objects.all().delete()[0]
        
        # 2. Clear orders
        deleted_counts['orders'] = Order.objects.all().delete()[0]
        
        # 3. Clear dropship imports
        deleted_counts['dropship_imports'] = DropshipImport.objects.all().delete()[0]
        
        # 4. Clear products
        deleted_counts['products'] = Product.objects.all().delete()[0]
        
        # 5. Clear shops
        deleted_counts['shops'] = Shop.objects.all().delete()[0]
        
        # 6. Clear users (this should be last)
        deleted_counts['users'] = User.objects.all().delete()[0]
        
        # Get final counts to verify
        final_counts = {
            'users': User.objects.count(),
            'shops': Shop.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'order_items': OrderItem.objects.count(),
            'dropship_imports': DropshipImport.objects.count(),
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Database cleared successfully',
            'initial_counts': initial_counts,
            'deleted_counts': deleted_counts,
            'final_counts': final_counts,
            'fully_clean': all(count == 0 for count in final_counts.values())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt  
@require_http_methods(["GET"])
def database_status(request):
    """
    Get current database status without authentication.
    
    GET /api/admin/database-status/
    """
    
    try:
        counts = {
            'users': User.objects.count(),
            'shops': Shop.objects.count(),
            'products': Product.objects.count(),
            'orders': Order.objects.count(),
            'order_items': OrderItem.objects.count(),
            'dropship_imports': DropshipImport.objects.count(),
        }
        
        return JsonResponse({
            'success': True,
            'counts': counts,
            'total_records': sum(counts.values()),
            'is_empty': all(count == 0 for count in counts.values())
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)