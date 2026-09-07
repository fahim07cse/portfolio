import os
import getpass

from supabase import create_client
from passlib.context import CryptContext
from dotenv import load_dotenv


# =========================
# LOAD ENVIRONMENT
# =========================

load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SERVICE_KEY = os.getenv(
    "SUPABASE_SERVICE_KEY"
)


if not SUPABASE_URL:
    raise RuntimeError(
        "SUPABASE_URL is missing"
    )


if not SUPABASE_SERVICE_KEY:
    raise RuntimeError(
        "SUPABASE_SERVICE_KEY is missing"
    )


# =========================
# SUPABASE
# =========================

supabase = create_client(
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
# CREATE ADMIN
# =========================

def create_admin():

    print()
    print("==============================")
    print(" CREATE PORTFOLIO ADMIN USER")
    print("==============================")
    print()


    username = input(
        "User ID: "
    ).strip().lower()


    if not username:

        print(
            "User ID cannot be empty."
        )

        return


    password = getpass.getpass(
        "Password: "
    )


    confirm_password = getpass.getpass(
        "Confirm Password: "
    )


    if not password:

        print(
            "Password cannot be empty."
        )

        return


    if password != confirm_password:

        print(
            "Passwords do not match."
        )

        return


    if len(password) < 8:

        print(
            "Password must be at least 8 characters."
        )

        return


    # =========================
    # CHECK EXISTING USER
    # =========================

    existing = (
        supabase
        .table("admin_users")
        .select("id, username")
        .eq(
            "username",
            username
        )
        .limit(1)
        .execute()
    )


    if existing.data:

        print()
        print(
            f'Admin "{username}" already exists.'
        )

        return


    # =========================
    # HASH PASSWORD
    # =========================

    password_hash = (
        password_context.hash(
            password
        )
    )


    # =========================
    # INSERT USER
    # =========================

    result = (
        supabase
        .table("admin_users")
        .insert({
            "username": username,
            "password_hash": password_hash,
            "role": "admin",
            "active": True
        })
        .execute()
    )


    if not result.data:

        print()
        print(
            "Admin could not be created."
        )

        return


    print()
    print("==============================")
    print(" ADMIN CREATED SUCCESSFULLY")
    print("==============================")
    print()
    print(
        f"User ID: {username}"
    )
    print(
        "Password stored securely as a hash."
    )
    print()


# =========================
# START
# =========================

if __name__ == "__main__":
    create_admin()
