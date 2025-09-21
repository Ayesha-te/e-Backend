import requests
import json

# Test shop list endpoint to see shop data format
try:
    response = requests.get('http://127.0.0.1:8000/api/shop/shops/')
    print(f'Shops list status: {response.status_code}')
    if response.status_code == 200:
        shops = response.json()
        for shop in shops:
            print(f'Shop: {shop.get("name")} - Logo URL: {shop.get("logo_url")}')
    else:
        print(f'Error response: {response.text}')
except Exception as e:
    print(f'Shop list error: {e}')

# Test my-shop endpoint without auth (should require auth)
try:
    response = requests.get('http://127.0.0.1:8000/api/shop/shops/my_shop/')
    print(f'\nMy-shop status: {response.status_code}')
    print(f'Response: {response.text}')
except Exception as e:
    print(f'My-shop error: {e}')