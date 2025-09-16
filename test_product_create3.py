import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Use existing user
login_data = {
    "username": "testvendor",
    "password": "testpass123"
}

response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
print("Login response:", response.status_code)

if response.status_code == 200:
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test with stock
    product_data = {
        "title": "Test Product with Stock",
        "price": 100.00,
        "stock": 50
    }

    response = requests.post(f"{BASE_URL}/shop/products/", json=product_data, headers=headers)
    print("Create product with stock response:", response.status_code, response.text)

    # Test with name and stock
    product_data2 = {
        "name": "Test Product with Name and Stock",
        "price": 200.00,
        "stock": 25
    }

    response = requests.post(f"{BASE_URL}/shop/products/", json=product_data2, headers=headers)
    print("Create product with name and stock response:", response.status_code, response.text)
else:
    print("Login failed")