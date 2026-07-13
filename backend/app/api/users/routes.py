from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.user import UserResponse
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

user_service = UserService()

@router.post("/",response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return user_service.create_user(db,user)

@router.get("/",response_model=list[UserResponse])
def get_user(
    db:Session = Depends(get_db)

):
    return user_service.get_user(db)

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
# starting with other backend stuffs