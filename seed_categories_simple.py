#!/usr/bin/env python3
"""
Simple script to seed default story categories
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.core.database import SessionLocal
from story.models import StoryCategory
import re
import uuid

def slugify(title: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title).lower()
    slug = re.sub(r'\s+', '-', slug).strip('-')
    return slug

def create_category_simple(db, name: str, description: str = None):
    """Create category without using schemas"""
    # Check for existing name
    existing_category = db.query(StoryCategory).filter(StoryCategory.name == name).first()
    if existing_category:
        print(f"⚠️  Category {name} already exists")
        return existing_category

    # Generate slug
    base_slug = slugify(name)
    unique_slug = base_slug
    while db.query(StoryCategory).filter(StoryCategory.slug == unique_slug).first():
        unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    db_category = StoryCategory(
        name=name,
        slug=unique_slug,
        description=description
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

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
                category = create_category_simple(
                    db, 
                    category_data["name"], 
                    category_data["description"]
                )
                print(f"✅ Created category: {category_data['name']}")
            except Exception as e:
                print(f"❌ Error creating category {category_data['name']}: {str(e)}")
        
        print("🎉 Categories seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding categories: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories() 