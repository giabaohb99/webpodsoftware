#!/usr/bin/env python3
"""
Script to seed default story categories
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.core.database import SessionLocal
from story.crud import create_category
from story.schemas import StoryCategoryCreate

def seed_categories():
    """Seed default story categories"""
    db = SessionLocal()
    
    default_categories = [
        {
            "name": "Tin tức",
            "description": "Các bài viết tin tức chung"
        },
        {
            "name": "Báo cáo",
            "description": "Các báo cáo và phân tích"
        },
        {
            "name": "Tuyển dụng",
            "description": "Thông tin tuyển dụng và việc làm"
        },
        {
            "name": "Hướng dẫn",
            "description": "Các bài hướng dẫn và tutorial"
        },
        {
            "name": "Công nghệ",
            "description": "Tin tức và bài viết về công nghệ"
        }
    ]
    
    try:
        for category_data in default_categories:
            try:
                category = StoryCategoryCreate(**category_data)
                create_category(db, category)
                print(f"✅ Created category: {category_data['name']}")
            except Exception as e:
                print(f"⚠️  Category {category_data['name']} might already exist: {str(e)}")
        
        print("🎉 Categories seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding categories: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories() 