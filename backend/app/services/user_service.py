from fastapi import HTTPException,status

from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserCreate

class UserService:
    def create_user(self, db: Session, user:UserCreate):
        existing_user = db.query(User).filter(User.email==user.email).first()
        if existing_user:
          raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

        db_user = User(email=user.email,full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user(self, db:Session):
       return db.query(User).all()
    def get_user_by_id(self , db:Session, user_id:int):
       
       user = db.query(User).filter(User.id==user_id).first()
       return user