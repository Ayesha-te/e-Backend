import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

# Use existing user
login_data = {
    "username": "testvendor",
    "password": "testpass123"
}

response = requests.post(f"{BASE_URL}/auth/token/", json=login_data)
print("Login response:", response.status_code, response.json())

if response.status_code == 200:
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Test with minimal data
    product_data = {
        "title": "Test Product 2",
        "price": 50.00
    }

    response = requests.post(f"{BASE_URL}/shop/products/", json=product_data, headers=headers)
    print("Create product response:", response.status_code, response.text)

    # Test with wrong field name
    product_data_wrong = {
        "name": "Test Product 3",
        "price": 75.00
    }

    response = requests.post(f"{BASE_URL}/shop/products/", json=product_data_wrong, headers=headers)
    print("Create product wrong field response:", response.status_code, response.text)
else:
    print("Login failed")