"""
Tests for scripts/manage_admin.py (task 1.5.7).

Uses an in-memory SQLite database with only the User table, so it needs no
Postgres and never touches Neon. Run from the repository root:

    python -m pytest backend/tests/test_manage_admin.py
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.security import verify_password
from backend.app.models.models import User
from scripts import manage_admin as cli

PROD_URL = "postgresql://wellqc_api:secret-pw@ep-divine-field-awwbazmn-pooler.c-12.us-east-1.aws.neon.tech/neondb"
DEV_URL = "postgresql://u:p@ep-tiny-haze-abc.c-12.us-east-1.aws.neon.tech/neondb"


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
    User.__table__.create(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
    engine.dispose()


def _add(db, email, role="USER", name="Test User"):
    user = User(email=email, name=name, passwordHash="x:y", role=role)
    db.add(user)
    db.commit()
    return user


# ------------------------------------------------------------ production guard
def test_guard_blocks_production_host_without_leaking_credentials():
    with pytest.raises(cli.CliError) as exc:
        cli.assert_safe_target(PROD_URL)
    assert "ep-divine-field" in str(exc.value)
    assert "secret-pw" not in str(exc.value)


def test_guard_allows_dev_host_and_returns_host_only():
    host = cli.assert_safe_target(DEV_URL)
    assert host.startswith("ep-tiny-haze")
    assert "p@" not in host


def test_guard_refuses_when_host_cannot_be_determined():
    with pytest.raises(cli.CliError):
        cli.assert_safe_target("")


def test_guard_honours_extra_blocked_hosts_from_environment(monkeypatch):
    monkeypatch.setenv(cli.EXTRA_BLOCKED_ENV, "ep-tiny-haze")
    with pytest.raises(cli.CliError):
        cli.assert_safe_target(DEV_URL)


def test_main_refuses_production_and_opens_no_session(monkeypatch):
    monkeypatch.setattr(cli.settings, "DATABASE_URL", PROD_URL, raising=False)

    def boom():
        raise AssertionError("a database session was opened against production")

    monkeypatch.setattr(cli, "SessionLocal", boom)
    assert cli.main(["list"]) == 2


# ------------------------------------------------------------------ role changes
def test_promote_changes_role_then_reports_no_change(db):
    _add(db, "a@example.com")
    assert cli.set_role(db, "a@example.com", "ADMIN") is True
    assert cli.set_role(db, "a@example.com", "ADMIN") is False
    assert db.query(User).one().role == "ADMIN"


def test_email_lookup_is_case_and_space_insensitive(db):
    _add(db, "Mixed@Example.com")
    assert cli.set_role(db, "  mixed@example.COM ", "ADMIN") is True


def test_unknown_email_is_an_error(db):
    with pytest.raises(cli.CliError):
        cli.set_role(db, "nobody@example.com", "ADMIN")


def test_invalid_role_is_an_error(db):
    _add(db, "a@example.com")
    with pytest.raises(cli.CliError):
        cli.set_role(db, "a@example.com", "SUPERUSER")


def test_cannot_demote_last_admin_without_force(db):
    _add(db, "boss@example.com", role="ADMIN")
    with pytest.raises(cli.CliError):
        cli.set_role(db, "boss@example.com", "USER")
    assert db.query(User).one().role == "ADMIN"
    assert cli.set_role(db, "boss@example.com", "USER", force=True) is True


def test_can_demote_an_admin_when_another_admin_exists(db):
    _add(db, "a@example.com", role="ADMIN")
    _add(db, "b@example.com", role=" admin ")  # stored with stray case and spaces
    assert cli.count_admins(db) == 2
    assert cli.set_role(db, "a@example.com", "USER") is True


# ------------------------------------------------------------------ create-admin
def test_create_admin_stores_verifiable_hash_and_verified_flag(db):
    user = cli.create_admin(db, "  New@Example.com ", " New Admin ", "a-long-enough-pw")
    saved = db.query(User).one()
    assert saved.id == user.id
    assert saved.email == "new@example.com"
    assert saved.name == "New Admin"
    assert saved.role == "ADMIN"
    assert saved.isEmailVerified is True
    assert saved.emailVerifiedAt is not None
    assert saved.passwordHash != "a-long-enough-pw"
    assert verify_password("a-long-enough-pw", saved.passwordHash)
    assert not verify_password("wrong-password!!", saved.passwordHash)


@pytest.mark.parametrize(
    "email,name,password",
    [
        ("not-an-email", "N", "a-long-enough-pw"),
        ("@example.com", "N", "a-long-enough-pw"),
        ("ok@example.com", "   ", "a-long-enough-pw"),
        ("ok@example.com", "N", "short"),
    ],
)
def test_create_admin_rejects_bad_input(db, email, name, password):
    with pytest.raises(cli.CliError):
        cli.create_admin(db, email, name, password)
    assert db.query(User).count() == 0


def test_create_admin_rejects_duplicate_email_case_insensitively(db):
    _add(db, "dup@example.com")
    with pytest.raises(cli.CliError):
        cli.create_admin(db, "DUP@example.com", "Dup", "a-long-enough-pw")
    assert db.query(User).count() == 1


# ------------------------------------------------------------------------ list
def test_list_users_can_filter_by_role(db):
    _add(db, "a@example.com", role="ADMIN")
    _add(db, "b@example.com")
    assert [u.email for u in cli.list_users(db, "ADMIN")] == ["a@example.com"]
    assert len(cli.list_users(db)) == 2
