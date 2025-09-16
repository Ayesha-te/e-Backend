import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Step 1: Signup as vendor
signup_data = {
    "username": "testvendor",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "vendor",
    "company_name": "Test Shop"
}

response = requests.post(f"{BASE_URL}/accounts/signup/", json=signup_data)
print("Signup response:", response.status_code, response.json())

# Step 2: Login to get token
login_data = {
    "username": "testvendor",
    "password": "testpass123"
}

response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
print("Login response:", response.status_code, response.json())

if response.status_code == 200:
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Step 3: Create product
    product_data = {
        "title": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "image_url": "https://example.com/image.jpg",
        "category": "Test Category"
    }

    response = requests.post(f"{BASE_URL}/shop/products/", json=product_data, headers=headers)
    print("Create product response:", response.status_code, response.text)
else:
    print("Login failed")