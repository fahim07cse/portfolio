from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os


app = FastAPI()


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://fahim07cse.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# ENVIRONMENT VARIABLES
# =========================

SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_SERVICE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY"
)

JWT_SECRET = os.getenv("JWT_SECRET")


if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is missing"
    )

if not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY is missing"
    )

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET is missing"
    )


# =========================
# SUPABASE CONNECTION
# =========================

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_KEY
)


# =========================
# PASSWORD HASHING
# =========================

password_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =========================
# REQUEST MODELS
# =========================

class LoginRequest(BaseModel):
    username: str
    password: str


# =========================
# JWT TOKEN
# =========================

def create_access_token(
    username: str,
    role: str
):

    expire = (
        datetime.now(timezone.utc)
        + timedelta(hours=8)
    )

    payload = {
        "sub": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET,
        algorithm="HS256"
    )

    return token


# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "status": "ok",
        "message": "Portfolio API is running"
    }


# =========================
# LOGIN
# =========================

@app.post("/api/login")
def login(request: LoginRequest):

    username = (
        request.username
        .strip()
        .lower()
    )


    result = (
        supabase
        .table("admin_users")
        .select(
            "id, username, password_hash, role, active"
        )
        .eq(
            "username",
            username
        )
        .limit(1)
        .execute()
    )


    if not result.data:

        raise HTTPException(
            status_code=401,
            detail="Invalid User ID or Password"
        )


    user = result.data[0]


    if not user["active"]:

        raise HTTPException(
            status_code=403,
            detail="Admin account is inactive"
        )


    password_ok = (
        password_context.verify(
            request.password,
            user["password_hash"]
        )
    )


    if not password_ok:

        raise HTTPException(
            status_code=401,
            detail="Invalid User ID or Password"
        )


    token = create_access_token(
        username=user["username"],
        role=user["role"]
    )


    return {
        "success": True,
        "username": user["username"],
        "role": user["role"],
        "access_token": token,
        "token_type": "bearer"
    }
