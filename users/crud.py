from sqlalchemy.orm import Session
from users import models, schemas
from core.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.Employee).filter(models.Employee.email == email).first()

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def create_user(db: Session, user: schemas.UserCreate):
    # Check if email already exists
    if get_user_by_email(db, email=user.employee.email):
        return None  # Or raise an exception

    # Create employee first
    db_employee = create_employee(db, employee=user.employee)
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        employee_id=db_employee.id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_login_time(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).update({"last_login": datetime.utcnow()})
    db.commit()

def create_user_session(db: Session, user_id: int, expires_in_days: int, device_info: str = None, ip_address: str = None):
    session_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    db_session = models.UserSession(
        user_id=user_id,
        session_token=session_token,
        expires_at=expires_at,
        device_info=device_info,
        ip_address=ip_address
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session 