from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
import sqlite3
import os
from pathlib import Path

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = "cricket-iq-secret-key-change-in-production"
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 7

# 👇 NAYA FIX: Render (Cloud) vs Local Path
if os.environ.get("RENDER"):
    DB_PATH = Path("/tmp/users.db")
else:
    DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "users.db"


# =========================================================
# Models
# =========================================================

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# =========================================================
# Database
# =========================================================

def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


# =========================================================
# Helpers
# =========================================================

def create_token(user_id: int, name: str, email: str) -> str:
    payload = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")


# =========================================================
# Endpoints
# =========================================================

@router.post("/signup")
def signup(req: SignupRequest):
    if len(req.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (req.email.lower(),)
        ).fetchone()

        if existing:
            raise HTTPException(400, "Email already registered")

        password_hash = pwd_context.hash(req.password)
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (req.name.strip(), req.email.lower(), password_hash)
        )
        conn.commit()

        return {"message": "Account created successfully"}

    finally:
        conn.close()


@router.post("/login")
def login(req: LoginRequest):
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (req.email.lower(),)
        ).fetchone()

        if not user or not pwd_context.verify(req.password, user["password_hash"]):
            raise HTTPException(401, "Invalid email or password")

        token = create_token(user["id"], user["name"], user["email"])

        return {
            "token": token,
            "name": user["name"],
            "email": user["email"]
        }

    finally:
        conn.close()


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"]
    }