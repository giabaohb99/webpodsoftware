from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from support.models import Support
from support.schemas import SupportCreate, SupportUpdate , SupportResponse
from story.models import Story
from file_storage.models import File
from core.core.email_service import email_service
import asyncio
import logging

# Configure logging
logger = logging.getLogger(__name__)

def create_support(db: Session, support_in: SupportCreate) -> Support:
    """
    Create a new support request
    """
    
    # Convert file_ids list to string if provided
    file_ids_str = None
    if support_in.file_ids:
        file_ids_str = ','.join(map(str, support_in.file_ids))
        logger.info(f"File IDs: {file_ids_str}")
    
    db_support = Support(
        title=support_in.title,
        content=support_in.content,
        email=support_in.email,
        fullname=support_in.fullname,
        support_type=support_in.support_type,
        source_type=support_in.source_type,
        source_id=support_in.source_id,
        file_ids=file_ids_str
    )
    
    db.add(db_support)
    db.commit()
    db.refresh(db_support)
    
    logger.info(f"✅ Support created successfully with ID: {db_support.id}")
    return db_support

async def create_support_with_notifications(
    db: Session, 
    support_in: SupportCreate
) -> SupportResponse:
    logger.info(f"Creating support with notifications: {support_in.title}")

    # Tạo bản ghi hỗ trợ
    support = create_support(db, support_in)
    user_name = support_in.fullname or support_in.email.split('@')[0]

    # Gửi email xác nhận cho người dùng
    await email_service.send_confirmation_email(
        to_email=support_in.email,
        user_name=user_name,
        support_id=support.id,
        support_type=support_in.support_type,
        content=support_in.content
    )

    # Parse file_ids từ chuỗi (nếu có)
    file_ids = [int(fid) for fid in support.file_ids.split(",")] if support.file_ids else []

    # Truy vấn thông tin file từ DB
    files = []
    attachments = []
    for file_id in file_ids:
        file = db.query(File).filter(File.id == file_id).first()
        if file:
            file_info = {
                "file_id": int(file_id),
                "filename": file.filename,
                "file_url": file.file_url
            }
            files.append(file_info)
            attachments.append({
                "file_id": file_id,
                "filename": file.filename,
                "size": f"{file.size / 1024:.1f}KB" if file.size else "Unknown"
            })

    # Gửi email cho admin
    await email_service.send_admin_support_notification(
        support_title=support.title,
        user_name=user_name,
        support_id=support.id,
        support_type=support_in.support_type,
        content=support_in.content,
        user_email=support_in.email,
        attachments=attachments
    )

    # Trả về phản hồi dạng chuẩn
    return SupportResponse(
        id=support.id,
        title=support.title,
        content=support.content,
        email=support.email,
        fullname=support.fullname,
        support_type=support.support_type,
        source_type=support.source_type,
        source_id=support.source_id,
        status=support.status,
        created_at=support.created_at,
        updated_at=support.updated_at,
        files=files
    )


def get_supports(
    db: Session, 
    skip: int = 0, 
    limit: int = 20, 
    keyword: Optional[str] = None,
    support_type: Optional[str] = None,
    status: Optional[str] = None,
    email: Optional[str] = None
) -> Tuple[List[Support], int]:
    """
    Retrieve supports with pagination and filtering
    """
    query = db.query(Support)
    
    if keyword:
        search_filter = or_(
            Support.title.ilike(f"%{keyword}%"),
            Support.content.ilike(f"%{keyword}%")
        )
        query = query.filter(search_filter)
    
    if support_type:
        query = query.filter(Support.support_type == support_type)
    
    if status:
        query = query.filter(Support.status == status)
    
    if email:
        query = query.filter(Support.email == email)
    
    total = query.count()
    supports = query.order_by(Support.created_at.desc()).offset(skip).limit(limit).all()
    # Parse file_ids for all supports
    for support in supports:
        if support.file_ids and isinstance(support.file_ids, str):
            support.file_ids = [int(fid) for fid in support.file_ids.split(',') if fid.strip().isdigit()]
        elif not support.file_ids:
            support.file_ids = []
    return supports, total

def get_support_by_id(db: Session, support_id: int) -> Optional[Support]:
    support = db.query(Support).filter(Support.id == support_id).first()
    if support and support.file_ids:
        if isinstance(support.file_ids, str):
            support.file_ids = [int(fid) for fid in support.file_ids.split(',') if fid.strip().isdigit()]
        # Lấy danh sách file object {filename, file_url}
        files = []
        from file_storage.models import File
        for file_id in support.file_ids:
            file = db.query(File).filter(File.id == file_id).first()
            if file:
                files.append({
                    'filename': file.filename,
                    'file_url': file.download_url
                })
        support.files = files
    else:
        support.files = []
        support.file_ids = []
    return support

def update_support(db: Session, support_id: int, support_update: SupportUpdate) -> Optional[Support]:
    support = get_support_by_id(db, support_id)
    if not support:
        return None
    
    update_data = support_update.dict(exclude_unset=True)
    
    # Convert file_ids list to string if provided
    if 'file_ids' in update_data and update_data['file_ids']:
        if isinstance(update_data['file_ids'], list):
            update_data['file_ids'] = ','.join(map(str, update_data['file_ids']))
    
    for field, value in update_data.items():
        setattr(support, field, value)
    
    db.commit()
    db.refresh(support)
    # Parse lại file_ids
    if support.file_ids and isinstance(support.file_ids, str):
        support.file_ids = [int(fid) for fid in support.file_ids.split(',') if fid.strip().isdigit()]
    elif not support.file_ids:
        support.file_ids = []
    return support

async def update_support_status(
    db: Session, 
    support_id: int, 
    new_status: str, 
    note: Optional[str] = None
) -> Optional[Support]:
    """
    Update support status and send notification email
    """
    logger.info(f"Updating support status: ID={support_id}, Status={new_status}")
    
    support = get_support_by_id(db, support_id)
    if not support:
        logger.error(f"Support not found with ID: {support_id}")
        return None
    
    old_status = support.status
    support.status = new_status
    
    db.commit()
    db.refresh(support)
    # Parse lại file_ids
    if support.file_ids and isinstance(support.file_ids, str):
        support.file_ids = [int(fid) for fid in support.file_ids.split(',') if fid.strip().isdigit()]
    elif not support.file_ids:
        support.file_ids = []
    logger.info(f"Status updated from {old_status} to {new_status}")
    
    # Send status update notification email
    status_messages = {
        'pending': 'đang chờ xử lý',
        'in_progress': 'đang được xử lý',
        'resolved': 'đã được giải quyết',
        'rejected': 'đã bị từ chối'
    }
    
    status_message = status_messages.get(new_status, new_status)
    
    # Send notification email to user
    logger.info(f"Sending status update email to: {support.email}")
    email_result = await email_service.send_notification_email(
        to_email=support.email,
        subject=f"Cập nhật trạng thái yêu cầu hỗ trợ #{support_id}",
        content=f"""
        <p>Yêu cầu hỗ trợ của bạn đã được cập nhật trạng thái:</p>
        <p><strong>Từ:</strong> {status_messages.get(old_status, old_status)}</p>
        <p><strong>Thành:</strong> {status_message}</p>
        {f'<p><strong>Ghi chú:</strong> {note}</p>' if note else ''}
        <p>Vui lòng kiểm tra lại yêu cầu của bạn trong hệ thống.</p>
        """,
        action_url=f"http://localhost:8000/support/{support_id}",
        additional_info=f"Support ID: {support_id}"
    )
    logger.info(f"Status update email result: {email_result}")
    
    return support

def delete_support(db: Session, support_id: int) -> bool:
    support = get_support_by_id(db, support_id)
    if not support:
        return False
    
    db.delete(support)
    db.commit()
    return True

def get_supports_by_source(
    db: Session, 
    source_type: str, 
    source_id: int
) -> List[Support]:
    """
    Get all support requests related to a specific source
    """
    supports = db.query(Support).filter(
        Support.source_type == source_type,
        Support.source_id == source_id
    ).order_by(Support.created_at.desc()).all()
    for support in supports:
        if support.file_ids and isinstance(support.file_ids, str):
            support.file_ids = [int(fid) for fid in support.file_ids.split(',') if fid.strip().isdigit()]
        elif not support.file_ids:
            support.file_ids = []
    return supports 