import requests
import json

def test_orders_endpoint():
    # Login to get token
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
                # Test orders list endpoint
                orders_url = "http://127.0.0.1:8000/api/shop/orders/list/"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                orders_response = requests.get(orders_url, headers=headers)
                print(f"Orders Status: {orders_response.status_code}")
                print(f"Orders Response: {orders_response.text}")
                
                if orders_response.status_code == 200:
                    print("✅ Orders endpoint working")
                else:
                    print("❌ Orders endpoint failed")
            else:
                print("❌ No access token received")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_orders_endpoint()