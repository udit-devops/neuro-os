from sqlalchemy.orm import Session
from app.models.users import User
from app.schemas.user import UserCreate

class UserService:
    def create_user(self, db: Session, user:UserCreate):
        db_user = User(email=user.email,full_name=user.full_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user