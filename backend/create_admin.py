import os
import getpass
from supabase import create_client
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is missing")
if not SUPABASE_SERVICE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_KEY is missing")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    print("\n==============================")
    print(" CREATE PORTFOLIO ADMIN USER")
    print("==============================\n")

    username = input("User ID: ").strip().lower()
    if not username:
        print("User ID cannot be empty.")
        return

    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")

    if not password:
        print("Password cannot be empty.")
        return
    if password != confirm_password:
        print("Passwords do not match.")
        return
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        return

    existing = (
        supabase.table("admin_users")
        .select("id, username")
        .eq("username", username)
        .limit(1)
        .execute()
    )
    if existing.data:
        print(f'\nAdmin "{username}" already exists.')
        return

    password_hash = password_context.hash(password)
    result = (
        supabase.table("admin_users")
        .insert({
            "username": username,
            "password_hash": password_hash,
            "role": "admin",
            "active": True,
        })
        .execute()
    )

    if not result.data:
        print("\nAdmin could not be created.")
        return

    print("\n==============================")
    print(" ADMIN CREATED SUCCESSFULLY")
    print("==============================")
    print(f"\nUser ID: {username}")
    print("Password stored securely as a hash.\n")

if __name__ == "__main__":
    create_admin()
