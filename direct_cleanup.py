import requests
import json

print("🧹 Database Cleanup - Direct Execution")
print("=" * 40)
print("This will DELETE ALL test data from your production database!")
print()

try:
    # Execute cleanup
    print("🗑️  Executing cleanup...")
    
    payload = {"secret": "CLEAR_ALL_TEST_DATA_2025"}
    
    response = requests.post(
        "https://e-backend-z33v.onrender.com/api/shop/admin/clear-database/",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            print("✅ Database cleared successfully!")
            print()
            print("📊 Summary:")
            print("Before cleanup:")
            for key, value in data["initial_counts"].items():
                print(f"   {key}: {value}")
            
            print("\nDeleted:")
            for key, value in data["deleted_counts"].items():
                print(f"   {key}: {value}")
            
            print("\nAfter cleanup:")
            for key, value in data["final_counts"].items():
                print(f"   {key}: {value}")
            
            if data["fully_clean"]:
                print("\n🎉 Database is completely clean!")
                print("🚀 Your app is ready for production users!")
            else:
                print("\n⚠️  Some data may still remain.")
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Connection Error: {e}")