from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

from core.core.database import get_db
from core.core.security import verify_password, create_access_token
from core.core.config import settings
from users import crud, schemas
from core.core.auth import (
    authenticate_user, 
    create_refresh_token, 
    get_current_user,
    get_password_hash
)
from core.core.exceptions import AuthenticationError
from jose import JWTError, jwt
from .models import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_username = crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    db_user_by_email = crud.get_user_by_email(db, email=user.employee.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Here you would typically send a verification email
    # For now, we'll just create the user directly.
    
    hashed_password = get_password_hash(user.password)
    created_user = crud.create_user(db=db, user=user, hashed_password=hashed_password)
    if not created_user:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user."
        )
    return created_user

@router.post("/login", response_model=schemas.Token)
def login_for_access_token(request: Request, db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise AuthenticationError(message="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Update last login time
    crud.update_user_login_time(db, user.id)

    # Create user session
    device_info = request.headers.get("User-Agent")
    ip_address = request.client.host
    crud.create_user_session(
        db, 
        user_id=user.id, 
        expires_in_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        device_info=device_info,
        ip_address=ip_address
    )

    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user.username, "type": "access"})
    refresh_token = create_refresh_token(data={"sub": user.username, "type": "refresh"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/token/refresh", response_model=schemas.Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    credentials_exception = AuthenticationError(
        message="Could not validate credentials",
    )
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
        
    # Create new access token
    new_access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token, # Or issue a new one
        "token_type": "bearer"
    }

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user