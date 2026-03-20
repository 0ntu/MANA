# Auth utilities: password hashing and JWT creation/validation
import hashlib

from app.database import users
from fastapi import Header, HTTPException, status
from bson import ObjectId
from jose import jwt, JWTError
from passlib.context import CryptContext

hashingUtil = CryptContext(schemes=["bcrypt"], deprecated="auto")

def _prepare_password(password: str) -> str:
    """SHA-256 pre-hash before bcrypt to bypass the 72-byte bcrypt limit."""
    return hashlib.sha256(password.encode()).hexdigest()

def make_formatted_userdata(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "current_energy": float(user.get("current_energy", 0.0)),
        "timestamp": user["timestamp"].isoformat() if user.get("timestamp") else None,
    }

# insecure lmao lolololol
jwt_secret = "asdf4739vnsjakfbcxvy3685474"

def create_jwt_token(subject: str) -> str:
    payload = {"sub": subject}
    return jwt.encode(payload, jwt_secret, algorithm="HS256")


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return payload.get("sub")
    except JWTError:
        return None


def validate_auth_user(authorization: str = Header(default="")) -> dict:
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization header in request",
        )

    token = authorization.split(" ", 1)[1].strip()
    user_id = decode_jwt_token(token)

    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def hash_password(password: str) -> str:
    return hashingUtil.hash(_prepare_password(password))

def check_hashed_password(password: str, hashed: str) -> bool:
    return hashingUtil.verify(_prepare_password(password), hashed)
