from app.db.database import Base
from sqlalchemy import Column, Integer, String , Boolean

class User(Base):
    __tablename__= "users"
    id= Column(Integer, primary_key=True, index=True)
   
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    phone_number = Column(String(20),nullable=True)
    hashed_password = Column(String(266))
    


