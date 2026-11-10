"""Promote an existing account to administrator without exposing credentials."""

import argparse

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote an existing PathForge account to administrator.")
    parser.add_argument("email", help="Email address used to register the account")
    arguments = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == arguments.email.strip().lower()))
        if user is None:
            parser.error("No account exists for that email. Register the account before promoting it.")
        user.role = "ADMIN"
        db.commit()
        print("Administrator access granted.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
