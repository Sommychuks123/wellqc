import os
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings

def get_engine_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    elif url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    return url

db_url = get_engine_url(settings.DATABASE_URL)

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 15},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Row-level security context (Sprint 5, Step 4, PR A)
#
# The database policies added later (PR B) read two transaction-local settings:
#   app.user_id   text, '' means "no user" (default-deny)
#   app.is_admin  'true' or 'false'
#
# They are set with set_config(..., true), i.e. per TRANSACTION, never per
# session, because the connection sits behind pgbouncer in transaction-pooling
# mode and a session-level SET would leak between requests.
#
# Until PR B enables the policies, setting these values changes nothing.
# ---------------------------------------------------------------------------
_SET_CTX = text(
    "select set_config('app.user_id', :u, true), set_config('app.is_admin', :a, true)"
)


def _ctx_params(session: Session) -> dict:
    return {
        "u": session.info.get("rls_user_id") or "",
        "a": "true" if session.info.get("rls_is_admin") else "false",
    }


@event.listens_for(SessionLocal, "after_begin")
def _apply_rls_context(session, transaction, connection):
    """Re-apply the context at the start of every transaction of this session
    (the first one, and any that follow a commit or rollback)."""
    if connection.dialect.name != "postgresql":
        return
    connection.execute(_SET_CTX, _ctx_params(session))


def set_rls_context(db: Session, user) -> None:
    """Record who the session acts for, and apply it to the open transaction.

    The admin flag comes from the verified User.role loaded from the database,
    never from anything the request supplies. Passing user=None (or never
    calling this) means no rows are visible once the policies exist.
    """
    is_admin = False
    user_id = ""
    if user is not None:
        user_id = str(user.id) if getattr(user, "id", None) is not None else ""
        is_admin = (getattr(user, "role", "") or "").strip().upper() == "ADMIN"

    db.info["rls_user_id"] = user_id
    db.info["rls_is_admin"] = is_admin

    # If a transaction is already open (the auth dependency's user lookup opened
    # it), after_begin will not fire again, so set the values on it directly.
    # If none is open yet, after_begin applies them when it starts.
    if db.get_bind().dialect.name == "postgresql" and db.in_transaction():
        db.execute(_SET_CTX, _ctx_params(db))


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
