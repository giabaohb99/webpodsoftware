#!/usr/bin/env python3
"""
Test script for email notifications
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_email_service():
    """Test email service directly"""
    try:
        from core.core.email_service import email_service
        
        print("Testing email service...")
        
        # Test sending confirmation email
        result = await email_service.send_confirmation_email(
            to_email="hb.giabao99@gmail.com",
            user_name="Huỳnh Gia Bảo",
            support_id=123,
            support_type="general",
            content="Test content"
        )
        
        print(f"Email result: {result}")
        
        if result:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email failed to send")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_email_service()) 