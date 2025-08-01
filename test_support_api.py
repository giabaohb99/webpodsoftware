import requests
import json

# Test data
test_data = {
    "title": "Test Support Request",
    "content": "This is a test support request to check email functionality",
    "email": "hb.giabao99@gmail.com",
    "fullname": "Huỳnh Gia Bảo",
    "support_type": "general"
}

# Test recruitment data
recruitment_data = {
    "title": "Ứng tuyển Frontend Developer",
    "content": "Tôi có 2 năm kinh nghiệm với React, TypeScript và Next.js. Mong được tham gia team.",
    "email": "hb.giabao99@gmail.com",
    "fullname": "Huỳnh Gia Bảo",
    "support_type": "recruitment",
    "file_ids": [1, 2]
}

def test_create_support():
    """Test creating a support request"""
    print("Testing create support...")
    
    response = requests.post(
        "http://localhost:8000/v1/support/public/",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        print("✅ Support created successfully!")
        return response.json()["id"]
    else:
        print("❌ Failed to create support")
        return None

def test_create_recruitment():
    """Test creating a recruitment application"""
    print("\nTesting create recruitment application...")
    
    response = requests.post(
        "http://localhost:8000/v1/support/public/recruitment/1",
        json=recruitment_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        print("✅ Recruitment application created successfully!")
        return response.json()["id"]
    else:
        print("❌ Failed to create recruitment application")
        return None

def test_get_supports():
    """Test getting support list"""
    print("\nTesting get supports...")
    
    response = requests.get("http://localhost:8000/v1/support/public/")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✅ Supports retrieved successfully!")
    else:
        print("❌ Failed to get supports")

if __name__ == "__main__":
    print("🚀 Testing Support API with fullname...")
    print("=" * 50)
    
    # Test 1: Create general support
    support_id = test_create_support()
    
    # Test 2: Create recruitment application
    recruitment_id = test_create_recruitment()
    
    # Test 3: Get supports list
    test_get_supports()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    
    if support_id:
        print(f"Support ID: {support_id}")
    if recruitment_id:
        print(f"Recruitment ID: {recruitment_id}")
    
    print("\n📧 Check the logs to see email sending status:")
    print("docker logs backend-fastapi-middlerware-app-1 --tail 100") 