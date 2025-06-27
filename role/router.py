from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from role.schemas import RoleCreate, RoleOut, UserRoleCreate, UserRoleOut
from role.crud import create_role, assign_role_to_user, get_roles, get_user_roles, seed_default_roles
from core.core.database import get_db

router = APIRouter(prefix="/role", tags=["Role"])

@router.post("/create", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role_api(role_in: RoleCreate, db: Session = Depends(get_db)):
    return create_role(db, role_in)

@router.post("/seed-default", status_code=201)
def seed_default_roles_api(db: Session = Depends(get_db)):
    seed_default_roles(db)
    return {"message": "Default roles seeded!"}

@router.get("/all", response_model=list[RoleOut])
def list_roles_api(db: Session = Depends(get_db)):
    return get_roles(db)

@router.post("/assign", response_model=UserRoleOut)
def assign_role_api(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    return assign_role_to_user(db, user_role.user_id, user_role.role_id)

@router.get("/user/{user_id}", response_model=list[UserRoleOut])
def get_user_roles_api(user_id: int, db: Session = Depends(get_db)):
    return get_user_roles(db, user_id) 