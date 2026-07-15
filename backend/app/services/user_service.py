from fastapi import HTTPException,status

from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserCreate, UserLogin
from app.schemas.user import UserUpdate
from app.core.security import hash_password, verify_password
class UserService:
    def create_user(self, db: Session, user:UserCreate):
        existing_user = db.query(User).filter(User.email==user.email).first()
        if existing_user:
          raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email already exists")

        db_user = User(email=user.email,full_name=user.full_name,hashed_password=hash_password(user.password))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def get_user(self, db:Session):
       return db.query(User).all()
    def get_user_by_id(self , db:Session, user_id:int):
       
       user = db.query(User).filter(User.id==user_id).first()
       return user
    
    def update_user(self, db:Session, user_id:int, user:UserUpdate):
       db_user = db.query(User).filter(User.id==user_id).first()
       if not db_user:
          raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="user not found"

          )
       
       db_user.full_name = user.full_name
       db.commit()
       db.refresh(db_user)
       return db_user
    
    def delete_user(self, db:Session, user_id:int):
       db_user = db.query(User).filter(User.id==user_id).first()
       if not db_user:
          raise HTTPException(
             status_code=status.HTTP_404_NOT_FOUND,
             detail="user not found"
          )
       db.delete(db_user)
       db.commit()

       return {"message": "user deleted successfully"}
    
    def user_login(self,db:Session,user:UserLogin):
       db_user = db.query(User).filter(User.email==user.email).first()
       if not db_user:
          raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Invalid email or password"
          )
       if not verify_password(user.password,db_user.hashed_password):
            raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid email or password"
            )
       return db_user
      