import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import logging
from jinja2 import Environment, FileSystemLoader, Template

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        from core.core.config import settings
        
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.admin_email = settings.ADMIN_EMAIL
        self.admin_support_email = settings.ADMIN_SUPPORT_EMAIL
        self.from_email = settings.FROM_EMAIL
        
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
        
        self.company_info = {
            'company_name': settings.COMPANY_NAME,
            'company_tagline': 'Hệ thống quản lý nội dung và tuyển dụng',
            'support_email': 'support@example.com',
            'support_phone': '0123-456-789',
            'working_hours': '8:00 - 18:00 (Thứ 2 - Thứ 6)',
            'current_year': datetime.now().year,
            'admin_dashboard_url': settings.ADMIN_DASHBOARD_URL
        }
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render Jinja2 template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context, **self.company_info)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            # Fallback to simple HTML
            return f"""
            <html>
            <body>
                <h2>Email Notification</h2>
                <p>Context: {context}</p>
                <p>Error: {str(e)}</p>
            </body>
            </html>
            """
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str, 
        text_content: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """
        Send email with detailed logging
        """
        try:
            logger.info(f"Starting to send email to {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
            logger.info(f"From: {self.from_email}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"noreply <{self.from_email}>"  # Sử dụng "noreply" thay vì email gốc
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add attachments if any
            if attachments:
                logger.info(f"Adding {len(attachments)} attachments")
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Send email
            logger.info("Connecting to SMTP server...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info("Starting TLS...")
                server.starttls()
                logger.info("Logging in to SMTP...")
                server.login(self.smtp_username, self.smtp_password)
                logger.info("Sending email...")
                server.send_message(msg)
                
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            logger.error(f"SMTP Details: {self.smtp_server}:{self.smtp_port}")
            logger.error(f"Username: {self.smtp_username}")
            logger.error(f"Error type: {type(e).__name__}")
            return False
    
    async def send_notification_email(self, to_email: str, subject: str, content: str, 
                                   action_url: Optional[str] = None, 
                                   additional_info: Optional[str] = None) -> bool:
        """
        Send notification email to admin using template
        """
        logger.info(f"Sending notification email to {to_email}")
        context = {
            'subject': subject,
            'content': content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action_url': action_url,
            'additional_info': additional_info
        }
        
        html_content = self._render_template('notification.html', context)
        result = await self.send_email(to_email, subject, html_content)
        logger.info(f"Notification email result: {result}")
        return result
    
    async def send_confirmation_email(self, to_email: str, user_name: str, support_id: int,
                                   support_type: str = "general", content: str = "",
                                   estimated_time: Optional[str] = None,
                                   dashboard_url: Optional[str] = None) -> bool:
        """
        Send confirmation email to user after submitting support request
        """
        logger.info(f"Sending confirmation email to {to_email} for support #{support_id}")
        subject = "Xác nhận yêu cầu hỗ trợ"
        context = {
            'user_name': user_name,
            'support_id': support_id,
            'support_type': support_type,
            'content': content,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending',
            'estimated_time': estimated_time or "1-2 ngày làm việc",
            'dashboard_url': dashboard_url or "http://localhost:8000/dashboard"
        }
        
        html_content = self._render_template('confirmation.html', context)
        result = await self.send_email(to_email, subject, html_content)
        return result
    
    async def send_recruitment_notification(self, story_title: str, author_name: str,
                                         story_description: Optional[str] = None,
                                         story_requirements: Optional[str] = None,
                                         admin_url: Optional[str] = None,
                                         edit_url: Optional[str] = None,
                                         additional_notes: Optional[str] = None) -> bool:
        """
        Send notification to admin when new recruitment post is created
        """
        logger.info(f"Sending recruitment notification to admin for story: {story_title}")
        subject = f"Thông báo tuyển dụng mới: {story_title}"
        context = {
            'story_title': story_title,
            'author_name': author_name,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'story_type': 'recruitment',
            'story_description': story_description,
            'story_requirements': story_requirements,
            'admin_url': admin_url or "http://localhost:8000/admin",
            'edit_url': edit_url or "http://localhost:8000/admin/edit",
            'additional_notes': additional_notes
        }
        
        html_content = self._render_template('recruitment_notification.html', context)
        result = await self.send_email(self.admin_email, subject, html_content)
        logger.info(f"Recruitment notification result: {result}")
        return result
    
    async def send_job_application_notification(self, support_title: str, user_name: str, 
                                             story_title: str, support_id: int,
                                             content: str = "", user_email: Optional[str] = None,
                                             attachments: Optional[List[dict]] = None,
                                             user_experience: Optional[str] = None,
                                             priority_level: Optional[str] = None) -> bool:
        """
        Send notification to admin when new job application is submitted
        """
        logger.info(f"Sending job application notification to admin for support #{support_id}")
        subject = f"Đơn ứng tuyển mới: {support_title}"
        context = {
            'support_title': support_title,
            'user_name': user_name,
            'story_title': story_title,
            'support_id': support_id,
            'content': content,
            'user_email': user_email,
            'attachments': attachments or [],
            'user_experience': user_experience,
            'priority_level': priority_level,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        html_content = self._render_template('job_application.html', context)
        result = await self.send_email(self.admin_support_email, subject, html_content)
        logger.info(f"Job application notification result: {result}")
        return result

    async def send_admin_support_notification(self, support_title: str, user_name: str, 
                                           support_id: int, support_type: str = "general",
                                           content: str = "", user_email: str = "",
                                           attachments: Optional[List[dict]] = None) -> bool:
        """
        Send notification to admin about new support request
        """
        logger.info(f"Sending admin support notification for support #{support_id}")
        subject = f"Yêu cầu hỗ trợ mới: {support_title}"
        
        # Add download URLs to attachments
        enhanced_attachments = []
        if attachments:
            for attachment in attachments:
                enhanced_attachment = attachment.copy()
                # Create download URL for the file
                if 'file_id' in attachment:
                    enhanced_attachment['download_url'] = f"http://localhost:8000/v1/files/{attachment['file_id']}/download"
                enhanced_attachments.append(enhanced_attachment)
        
        context = {
            'support_title': support_title,
            'user_name': user_name,
            'support_id': support_id,
            'support_type': support_type,
            'content': content,
            'user_email': user_email,
            'attachments': enhanced_attachments,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'pending'
        }
        
        html_content = self._render_template('admin_notification.html', context)
        result = await self.send_email(self.admin_support_email, subject, html_content)
        logger.info(f"Admin support notification result: {result}")
        return result

# Create global instance
email_service = EmailService() 