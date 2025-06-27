from sqlalchemy.orm import Session
from role.models import Role, UserRole
from role.schemas import RoleCreate, UserRoleCreate, DEFAULT_ROLES

# Tạo role mới
def create_role(db: Session, role_in: RoleCreate):
    db_role = Role(name=role_in.name, description=role_in.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# Khởi tạo các quyền mẫu nếu chưa có
def seed_default_roles(db: Session):
    for role in DEFAULT_ROLES:
        if not db.query(Role).filter_by(name=role["name"]).first():
            db.add(Role(name=role["name"], description=role["description"]))
    db.commit()

# Gán role cho user
def assign_role_to_user(db: Session, user_id: int, role_id: int):
    user_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(user_role)
    db.commit()
    db.refresh(user_role)
    return user_role

# Lấy tất cả role
def get_roles(db: Session):
    return db.query(Role).all()

# Lấy role của user
def get_user_roles(db: Session, user_id: int):
    """
    Returns a list of Role objects that the user has.
    """
    return db.query(Role).join(UserRole).filter(UserRole.user_id == user_id).all() 