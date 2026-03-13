#auth 
from app.database import users
from fastapi import Header, HTTPException, status #handle auth http requests
from bson import ObjectId  #get jwt tokens for the user ids
from jose import jwt, JWTError #jwt handles and api for keeping logged in
from passlib.context import CryptContext #hashing

hashingUtil = CryptContext(schemes=["bcrypt"], deprecated="auto") #hash pass during signup and validate login

def make_formatted_userdata(user:dict) -> dict: #user docs
  return{"id": str(user["_id"]), "username": user["username"], "current_energy": float(user.get("current_energy", 0.0)), "timestamp": user["created_at"].isoformat()}


jwt_hashing = "asdf4739vnsjakfbcxvy3685474" #this should be a env var in a realistic environment (secret hashing key) maybe we do for sprint2

def create_jwt_token(subject: str) -> str: #and encode
  payload = {"sub": subject};
  return jwt.encode(payload, jwt_hashing, algorithm="HS256")

def decode_jwt_token(token: str):
  try:
    payload = jwt.decode(token, jwt_hashing, algorithms=["HS256"])
    return payload.get("sub")
  except JWTError:
    return None

#actual check got framework but goign to bed quick done tom
def validate_auth_user(authorization: str = Header(default="")) -> dict: #intake fastapi HTTP header of auth from frontend request
  if (not authorization.startswith("Bearer ")):  #formatted as Authorization: Bearer (auth code)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no authorization header in request")
  
  token = authorization.split(" ", 1)[1].strip() #grab token from header
  userID = decode_jwt_token(token)
  if (not ObjectId.is_valid(userID) or userID == ""):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="decode token error, bad userID")
  
  user = users.find_one({"_id": ObjectId(userID)})
  if (not user):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="no user found")
  
  return user

def hash_password(password: str) -> str:
  return hashingUtil.hash(password)

def check_hashed_password(password: str, hash_pass: str) -> bool;
  return hashingUtil.verify(password, hash_pass)
