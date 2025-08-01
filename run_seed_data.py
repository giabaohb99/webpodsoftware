#!/usr/bin/env python3
"""
Script to run SQL seed data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.core.database import SessionLocal
import subprocess

def run_sql_seed():
    """Run SQL seed data using docker exec"""
    print("🌱 Running SQL Seed Data")
    print("=" * 40)
    
    try:
        # Read SQL file
        with open('seed_data.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Execute SQL in container
        cmd = [
            'docker', 'exec', '-i', 
            'backend-fastapi-middlerware-db-1',
            'mysql', '-u', 'user', '-ppassword', 'users_db'
        ]
        
        print("📊 Executing SQL seed data...")
        result = subprocess.run(
            cmd,
            input=sql_content.encode('utf-8'),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ SQL seed data executed successfully!")
            print("📋 Sample data created:")
            print("   - 4 users (admin, story_manager, user1, user2)")
            print("   - 4 employees")
            print("   - 3 roles (admin, story_manager, user)")
            print("   - 5 stories (2 recruitment, 2 articles, 1 report)")
            print("   - 5 support requests")
            print("   - 3 files")
            print("   - File attachments linked")
        else:
            print("❌ Error executing SQL seed data:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ Error: seed_data.sql file not found")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def check_data():
    """Check if data was created successfully"""
    print("\n🔍 Checking created data...")
    
    try:
        # Test API endpoints
        import requests
        
        # Check categories
        response = requests.get("http://localhost:8000/v1/story/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Found {len(categories)} categories")
        
        # Check stories
        response = requests.get("http://localhost:8000/v1/story/public/")
        if response.status_code == 200:
            stories = response.json()
            print(f"✅ Found {stories['total']} stories")
            
            # Show story types
            story_types = {}
            for story in stories['items']:
                story_type = story.get('story_type', 'unknown')
                story_types[story_type] = story_types.get(story_type, 0) + 1
            
            print("📊 Story types distribution:")
            for story_type, count in story_types.items():
                print(f"   - {story_type}: {count}")
        
        print("\n🎉 Data check completed!")
        
    except Exception as e:
        print(f"❌ Error checking data: {str(e)}")

if __name__ == "__main__":
    run_sql_seed()
    check_data() 