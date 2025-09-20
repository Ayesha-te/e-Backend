import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create a test dropshipper user with known credentials
try:
    test_user = User.objects.create_user(
        username='testdropshipper',
        email='test@example.com',
        password='testpass123',
        role='dropshipper'
    )
    print(f"Created test user: {test_user.username} with role {test_user.role}")
except Exception as e:
    print(f"User might already exist: {e}")
    
    # Try to get existing user
    try:
        test_user = User.objects.get(username='testdropshipper')
        test_user.set_password('testpass123')
        test_user.save()
        print(f"Updated password for existing user: {test_user.username}")
    except User.DoesNotExist:
        print("User doesn't exist and couldn't be created")