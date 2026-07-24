from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime,timedelta,timezone 
from pwdlib import PasswordHash
from app.core.config import settings
from fastapi import Depends , HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
password_hasher = PasswordHash.recommended()
ALGORITHM = "HS256"
    
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=30)
    to_encode["exp"] = expire
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=ALGORITHM)

def get_current_user(
        token:str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("sub")
        if  user_id is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
        db_user = db.query(User).filter(User.id==int(user_id)).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
       
        return db_user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")