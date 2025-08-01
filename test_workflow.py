#!/usr/bin/env python3
"""
Test script to demonstrate the complete workflow
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_workflow():
    print("🚀 Testing Complete Workflow")
    print("=" * 50)
    
    # 1. Test Categories API
    print("\n1. Testing Categories API...")
    try:
        response = requests.get(f"{BASE_URL}/v1/story/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories:")
            for cat in categories:
                print(f"   - {cat['name']} (ID: {cat['id']})")
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting categories: {str(e)}")
    
    # 2. Test Public Stories API
    print("\n2. Testing Public Stories API...")
    try:
        response = requests.get(f"{BASE_URL}/v1/story/public/")
        if response.status_code == 200:
            stories = response.json()
            print(f"✅ Found {stories['total']} stories")
        else:
            print(f"❌ Failed to get stories: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stories: {str(e)}")
    
    # 3. Test Support API (without auth for now)
    print("\n3. Testing Support API...")
    try:
        response = requests.get(f"{BASE_URL}/v1/support/")
        print(f"📊 Support API response: {response.status_code}")
        if response.status_code == 401:
            print("   (Expected: Requires authentication)")
    except Exception as e:
        print(f"❌ Error testing support API: {str(e)}")
    
    # 4. Test API Documentation
    print("\n4. Testing API Documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API Documentation available at: http://localhost:8000/docs")
        else:
            print(f"❌ Failed to get docs: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting docs: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Workflow Test Completed!")
    print("\n📋 Next Steps:")
    print("1. Visit http://localhost:8000/docs for API documentation")
    print("2. Use Adminer at http://localhost:8080 to view database")
    print("3. Test with authentication tokens")
    print("4. Test email notifications")

if __name__ == "__main__":
    test_workflow() 