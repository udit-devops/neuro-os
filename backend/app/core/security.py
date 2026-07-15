import jwt
from datetime import datetime,timedelta,timezone 
from pwdlib import PasswordHash
from app.core.config import settings
password_hasher = PasswordHash.recommended()
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)

def create_access_token(data:dict,secret_key:str,algorithm:str):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=30)
    to_encode["exp"] = expire
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=ALGORITHM)

    
