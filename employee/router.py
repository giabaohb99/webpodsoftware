from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from employee.schemas import EmployeeCreate, Employee
from employee.crud import create_employee
from core.core.database import get_db

router = APIRouter(prefix="/employee", tags=["Employee"])

@router.post("/create", response_model=Employee, status_code=status.HTTP_201_CREATED)
def create_employee_api(employee_in: EmployeeCreate, db: Session = Depends(get_db)):
    try:
        employee = create_employee(db, employee_in)
        return employee
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 