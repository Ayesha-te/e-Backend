import requests
import json

def test_order_endpoint():
    url = "http://127.0.0.1:8000/api/shop/orders/list/"
    
    try:
        response = requests.get(url, headers={"Content-Type": "application/json"})
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ JSON Response: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server might not be running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_order_endpoint()