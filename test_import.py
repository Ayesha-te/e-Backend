import requests
import json

def test_import_endpoint():
    # First, let's get a valid JWT token for authentication
    login_url = "http://127.0.0.1:8000/api/auth/token/"
    login_data = {
        "username": "testdropshipper",  # Using test user
        "password": "testpass123"  # Known password
    }
    
    try:
        # Login to get token
        login_response = requests.post(login_url, json=login_data)
        print(f"Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get('access')
            
            if access_token:
                # Test import endpoint
                import_url = "http://127.0.0.1:8000/api/shop/products/15/import_to_my_shop/"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                import_response = requests.post(import_url, headers=headers)
                print(f"Import Status: {import_response.status_code}")
                print(f"Import Response: {import_response.text}")
                
                if import_response.status_code != 200 and import_response.status_code != 201:
                    print("❌ Import failed")
                else:
                    print("✅ Import successful")
            else:
                print("❌ No access token received")
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_import_endpoint()