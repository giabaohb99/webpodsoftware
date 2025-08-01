#!/usr/bin/env python3
"""
Test script for email templates
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.core.email_service import email_service

async def test_email_templates():
    """Test both user confirmation and admin notification email templates"""
    
    print("🧪 Testing Email Templates...")
    print("=" * 50)
    
    # Test 1: User Confirmation Email
    print("\n📧 Test 1: User Confirmation Email")
    print("-" * 30)
    
    user_result = await email_service.send_confirmation_email(
        to_email="test@example.com",
        user_name="Nguyễn Văn A",
        support_id=123,
        support_type="general",
        content="Tôi cần hỗ trợ về vấn đề đăng nhập vào hệ thống.",
        estimated_time="1-2 ngày làm việc"
    )
    
    print(f"User confirmation email result: {user_result}")
    
    # Test 2: Admin Notification Email
    print("\n📧 Test 2: Admin Notification Email")
    print("-" * 30)
    
    admin_result = await email_service.send_admin_support_notification(
        support_title="Yêu cầu hỗ trợ đăng nhập",
        user_name="Nguyễn Văn A",
        support_id=123,
        support_type="general",
        content="Tôi cần hỗ trợ về vấn đề đăng nhập vào hệ thống.",
        user_email="test@example.com",
        attachments=[
            {"file_id": 1, "filename": "screenshot.png", "size": "245.3KB"},
            {"file_id": 2, "filename": "error_log.txt", "size": "12.1KB"}
        ]
    )
    
    print(f"Admin notification email result: {admin_result}")
    
    # Test 3: Recruitment Application Email
    print("\n📧 Test 3: Recruitment Application Email")
    print("-" * 30)
    
    recruitment_result = await email_service.send_admin_support_notification(
        support_title="Ứng tuyển Frontend Developer",
        user_name="Trần Thị B",
        support_id=124,
        support_type="recruitment",
        content="Tôi có 3 năm kinh nghiệm với React, TypeScript và Next.js. Mong được tham gia team.",
        user_email="candidate@example.com",
        attachments=[
            {"file_id": 3, "filename": "CV_Trần_Thị_B.pdf", "size": "1.2MB"},
            {"file_id": 4, "filename": "portfolio.pdf", "size": "3.5MB"}
        ]
    )
    
    print(f"Recruitment application email result: {recruitment_result}")
    
    print("\n" + "=" * 50)
    print("✅ Email template testing completed!")
    print("\n📋 Check the logs to see email sending status:")
    print("docker logs backend-fastapi-middlerware-app-1 --tail 50")

if __name__ == "__main__":
    asyncio.run(test_email_templates()) 