from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime,timedelta,timezone 
from pwdlib import PasswordHash
from app.core.config import settings
from fastapi import Depends , HTTPException, status, Header
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

def _local_user(db: Session) -> "User":
    email = "local@neuroos.local"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            full_name="Local User",
            is_active=True,
            hashed_password=hash_password("local"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_token_or_none(
    authorization: str | None = Header(default=None),
) -> str | None:
    if settings.AUTH_DISABLED:
        return None
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return authorization.split(" ", 1)[1].strip()

def get_current_user(
        token: str | None = Depends(get_token_or_none),
        db: Session = Depends(get_db)
):
    if settings.AUTH_DISABLED:
        return _local_user(db)
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