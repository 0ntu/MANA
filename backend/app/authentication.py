#auth 
from app.database import users_collection
from fastapi import Header, HTTPException, status #handle auth http requests
from bson import ObjectId  #get jwt tokens for the user ids
from jose import jwt, JWTError #jwt handles and api for keeping logged in
from passlib.context import CryptContext #hashing


def create_access_token(subject: str) -> str:
  payload = {"sub": subject};
  return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str):
  try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload.get("sub")
  except JWTError:
    return None

#actual check got framework but goign to bed quick done tom


#def hash plus pwd context and keys
def check_hashed_password(pass: str, hash_pass: str) -> bool;
  return pwd_context.verify(pass, hash_pass)
