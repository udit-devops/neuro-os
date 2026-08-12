from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserLogin
from app.core.security import get_current_user
from app.models.users import User
from app.schemas.user import UserResponse , Token
from app.core.rate_limit import limiter
from fastapi.security import OAuth2PasswordRequestForm
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_service = UserService()

@router.post("/",response_model=UserResponse)
@limiter.limit("30/minute")
def create_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return user_service.create_user(db,user)

@router.get("/",response_model=list[UserResponse])
def get_user(
    db:Session = Depends(get_db)

):
    return user_service.get_user(db)

@router.get("/me",response_model=UserResponse)
def get_current_user_info(
    current_user:User = Depends(get_current_user)
):
    return current_user
@router.get("/{user_id}",response_model=UserResponse)
def get_user_by_id(
    user_id:int,
    db:Session = Depends(get_db)
):
    return user_service.get_user_by_id(db,user_id)

@router.put("/{user_id}",response_model=UserResponse)
def update_user(
    user_id:int,
    user:UserUpdate,
    db:Session = Depends(get_db)
):
    
    return user_service.update_user(db,user_id,user)


@router.delete("/{user_id}",response_model=dict)
def delete_user(
    user_id:int,
    db:Session = Depends(get_db)
):
    return user_service.delete_user(db,user_id)

@router.post("/login",response_model=Token)
@limiter.limit("30/minute")
def user_login(
  request: Request,
  form_data: OAuth2PasswordRequestForm = Depends(),
  db:Session = Depends(get_db)
):
    return user_service.user_login(db,form_data)

