from sqlalchemy.orm import Session
from employee.models import Employee
from users.models import User
from employee.schemas import EmployeeCreate
from core.core.security import get_password_hash
from datetime import datetime

def create_employee(db: Session, employee_in: EmployeeCreate):
    # 1. Create user
    user_data = employee_in.user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    db.add(db_user)
    db.flush()  # Assigns id

    # 2. Create employee
    db_employee = Employee(
        user_id=db_user.id,
        first_name=employee_in.first_name,
        last_name=employee_in.last_name,
        email=employee_in.email,
        phone_number=employee_in.phone_number,
        address=employee_in.address,
        date_of_birth=employee_in.date_of_birth,
        status=employee_in.status or 1
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee 