import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

users = User.objects.all()
print(f"Total users: {users.count()}")

for user in users:
    print(f"- ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}")
    
# If no users exist, create a test user
if users.count() == 0:
    print("\nCreating test user...")
    test_user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        role='dropshipper'
    )
    print(f"Created test user: {test_user.username} with role {test_user.role}")
else:
    print("\nUsers exist in database.")