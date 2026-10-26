#!/usr/bin/env python3
"""
Interactive admin management CLI (schedule task 1.5.7).

Run from the repository root, against the DEV database only:

    python scripts/manage_admin.py                      # interactive menu
    python scripts/manage_admin.py list [--role ADMIN]
    python scripts/manage_admin.py promote user@example.com
    python scripts/manage_admin.py demote user@example.com [--force]
    python scripts/manage_admin.py create-admin user@example.com --name "Full Name"

Rules built in (owner decisions, Oct 25):
  * Refuses to run when DATABASE_URL points at the production host
    (ep-divine-field). There is no override flag.
  * Passwords are only ever typed at a hidden prompt, never passed as an
    argument (shell history).
  * Demoting the last remaining ADMIN is refused unless --force is given.
  * Prints only the database HOST, never credentials.

Not done by design: this script does not write ActivityLog rows (the
ActivityLog columns were not reviewed when it was written).
"""
from __future__ import annotations

import argparse
import getpass
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import func  # noqa: E402

from backend.app.core.config import settings  # noqa: E402
from backend.app.core.database import SessionLocal  # noqa: E402
from backend.app.core.security import hash_password  # noqa: E402
from backend.app.models.models import User  # noqa: E402

BLOCKED_HOST_MARKERS = ("ep-divine-field",)
EXTRA_BLOCKED_ENV = "WELLQC_BLOCKED_DB_HOSTS"  # optional, comma-separated
MIN_PASSWORD_LENGTH = 12
ROLES = ("ADMIN", "USER")


class CliError(Exception):
    """A refusal or validation failure that should be shown to the operator."""


# ---------------------------------------------------------------- safety guard
def db_host(url: Optional[str]) -> str:
    try:
        return (urlparse(url or "").hostname or "").lower()
    except ValueError:
        return ""


def assert_safe_target(url: Optional[str] = None) -> str:
    """Return the DB host if it is safe to use, else raise CliError."""
    host = db_host(url if url is not None else settings.DATABASE_URL)
    if not host:
        raise CliError("Cannot tell which database DATABASE_URL points at; refusing to run.")
    markers = list(BLOCKED_HOST_MARKERS)
    extra = os.environ.get(EXTRA_BLOCKED_ENV, "")
    markers += [m.strip().lower() for m in extra.split(",") if m.strip()]
    for marker in markers:
        if marker in host:
            raise CliError(
                f"Refusing to run: DATABASE_URL points at a blocked host ({marker}). "
                "This tool is for the dev database only."
            )
    return host


# ------------------------------------------------------------------ operations
def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def is_admin(user: User) -> bool:
    return (user.role or "").strip().upper() == "ADMIN"


def find_user(db, email: str) -> User:
    user = db.query(User).filter(func.lower(User.email) == normalize_email(email)).first()
    if user is None:
        raise CliError(f"No user with email {normalize_email(email)!r}.")
    return user


def count_admins(db) -> int:
    return db.query(User).filter(func.upper(func.trim(User.role)) == "ADMIN").count()


def list_users(db, role: Optional[str] = None) -> List[User]:
    query = db.query(User)
    if role:
        query = query.filter(func.upper(func.trim(User.role)) == role.strip().upper())
    return query.order_by(User.createdAt).all()


def set_role(db, email: str, role: str, force: bool = False) -> bool:
    """Set a user's role. Returns True if changed, False if already that role."""
    role = role.upper()
    if role not in ROLES:
        raise CliError(f"Role must be one of {ROLES}.")
    user = find_user(db, email)
    if (user.role or "").strip().upper() == role:
        return False
    if role == "USER" and is_admin(user) and count_admins(db) <= 1 and not force:
        raise CliError("Refusing to demote the last ADMIN (use --force to override).")
    user.role = role
    db.commit()
    return True


def create_admin(db, email: str, name: str, password: str) -> User:
    email = normalize_email(email)
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise CliError("That does not look like an email address.")
    if not (name or "").strip():
        raise CliError("A name is required.")
    if len(password or "") < MIN_PASSWORD_LENGTH:
        raise CliError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if db.query(User).filter(func.lower(User.email) == email).first() is not None:
        raise CliError(f"A user with email {email!r} already exists (use promote instead).")
    user = User(
        email=email,
        name=name.strip(),
        passwordHash=hash_password(password),
        role="ADMIN",
        isEmailVerified=True,
        emailVerifiedAt=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(user)
    db.commit()
    return user


# ------------------------------------------------------------------- terminal
def _confirm(prompt: str, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    return input(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")


def _print_users(users: List[User]) -> None:
    if not users:
        print("No users.")
        return
    print(f"{'EMAIL':40} {'ROLE':8} {'VERIFIED':8} NAME")
    for u in users:
        print(f"{u.email[:40]:40} {(u.role or '').strip().upper():8} {str(bool(u.isEmailVerified)):8} {u.name}")
    print(f"({len(users)} users)")


def _prompt_new_password() -> str:
    first = getpass.getpass("Password (hidden): ")
    second = getpass.getpass("Repeat password: ")
    if first != second:
        raise CliError("Passwords did not match.")
    return first


def _run(db, args) -> None:
    if args.command == "list":
        _print_users(list_users(db, args.role))
    elif args.command in ("promote", "demote"):
        role = "ADMIN" if args.command == "promote" else "USER"
        user = find_user(db, args.email)
        if not _confirm(f"Set {user.email} to {role}?", args.yes):
            print("Cancelled.")
            return
        print("Done." if set_role(db, args.email, role, force=getattr(args, "force", False)) else "No change (already that role).")
    elif args.command == "create-admin":
        name = args.name or input("Full name: ")
        if not _confirm(f"Create ADMIN account for {normalize_email(args.email)}?", args.yes):
            print("Cancelled.")
            return
        user = create_admin(db, args.email, name, _prompt_new_password())
        print(f"Created admin {user.email}.")


def _menu(db) -> None:
    while True:
        print("\n1) List users  2) Promote to ADMIN  3) Demote to USER  4) Create admin  5) Quit")
        choice = input("Choose: ").strip()
        try:
            if choice == "1":
                _print_users(list_users(db))
            elif choice in ("2", "3"):
                email = input("User email: ")
                _run(db, argparse.Namespace(command="promote" if choice == "2" else "demote", email=email, yes=False, force=False))
            elif choice == "4":
                _run(db, argparse.Namespace(command="create-admin", email=input("Email: "), name=None, yes=False))
            elif choice == "5":
                return
            else:
                print("Please enter 1 to 5.")
        except CliError as exc:
            print(f"Error: {exc}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Admin management (dev database only).")
    parser.add_argument("--yes", action="store_true", help="skip confirmation prompts")
    sub = parser.add_subparsers(dest="command")
    p = sub.add_parser("list", help="list users")
    p.add_argument("--role", choices=ROLES)
    for name in ("promote", "demote"):
        p = sub.add_parser(name, help=f"{name} a user")
        p.add_argument("email")
        if name == "demote":
            p.add_argument("--force", action="store_true", help="allow demoting the last ADMIN")
    p = sub.add_parser("create-admin", help="create a new ADMIN account")
    p.add_argument("email")
    p.add_argument("--name")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        host = assert_safe_target()  # before any connection is opened
    except CliError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(f"Target database host: {host}")
    db = SessionLocal()
    try:
        if args.command is None:
            _menu(db)
        else:
            _run(db, args)
        return 0
    except CliError as exc:
        db.rollback()
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
