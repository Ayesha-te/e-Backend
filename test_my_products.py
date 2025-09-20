import requests
import json

def test_my_products_for_dropshipper():
    # Login as the test dropshipper
    login_url = "http://127.0.0.1:8000/api/auth/token/"
    login_data = {
        "username": "testdropshipper",
        "password": "testpass123"
    }
    
    try:
        # Login
        login_response = requests.post(login_url, json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            if access_token:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # First, import a product if not already imported
                print("\n1. Importing product 15...")
                import_response = requests.post(
                    "http://127.0.0.1:8000/api/shop/products/15/import_to_my_shop/",
                    headers=headers
                )
                print(f"Import Status: {import_response.status_code}")
                print(f"Import Response: {import_response.text}")
                
                # Now test my_products endpoint
                print("\n2. Testing my_products endpoint...")
                my_products_response = requests.get(
                    "http://127.0.0.1:8000/api/shop/products/my_products/",
                    headers=headers
                )
                print(f"My Products Status: {my_products_response.status_code}")
                
                if my_products_response.status_code == 200:
                    products = my_products_response.json()
                    print(f"Number of products returned: {len(products)}")
                    
                    if products:
                        print("Sample product:")
                        product = products[0]
                        print(f"  ID: {product.get('id')}")
                        print(f"  Title: {product.get('title')}")
                        print(f"  Vendor: {product.get('vendor_name')}")
                        print(f"  Shop: {product.get('shop_name')}")
                        print("✅ Dropshipper can see imported products!")
                    else:
                        print("❌ No products returned for dropshipper")
                else:
                    print(f"❌ My Products failed: {my_products_response.text}")
            else:
                print("❌ No access token received")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_my_products_for_dropshipper()