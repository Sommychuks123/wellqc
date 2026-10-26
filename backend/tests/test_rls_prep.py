import pytest
from unittest.mock import MagicMock, patch
from fastapi import Request
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user_optional
from backend.app.models.models import User
from backend.app.services.standardiser import (
    CustomAliasEntry,
    get_custom_aliases,
    set_custom_aliases,
    standardise_mnemonic,
    add_custom_alias,
    edit_custom_alias,
    remove_custom_alias,
)

client = TestClient(app)


def test_change3_reset_token_dev_only(monkeypatch):
    """Change 3: Make the reset-token gate dev-only.
    resetToken is returned only when settings.ENVIRONMENT == 'development'.
    """
    mock_user = MagicMock()
    mock_user.id = "test-uid-123"
    mock_user.email = "geologist@example.com"
    mock_user.name = "Test Geologist"
    mock_user.role = "PETROPHYSICIST"

    def override_get_db():
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        # 1. Environment is 'development' -> resetToken should be returned
        monkeypatch.setattr(settings, "ENVIRONMENT", "development")
        res_dev = client.post("/api/auth/forgot-password", json={"email": "geologist@example.com"})
        assert res_dev.status_code == 200
        assert res_dev.json().get("success") is True
        assert "resetToken" in res_dev.json()
        assert res_dev.json()["resetToken"] is not None

        # 2. Environment is 'production' -> resetToken must NEVER be returned
        monkeypatch.setattr(settings, "ENVIRONMENT", "production")
        res_prod = client.post("/api/auth/forgot-password", json={"email": "geologist@example.com"})
        assert res_prod.status_code == 200
        assert res_prod.json().get("success") is True
        assert "resetToken" not in res_prod.json()

        # 3. Environment is 'staging' -> resetToken must NEVER be returned
        monkeypatch.setattr(settings, "ENVIRONMENT", "staging")
        res_staging = client.post("/api/auth/forgot-password", json={"email": "geologist@example.com"})
        assert res_staging.status_code == 200
        assert res_staging.json().get("success") is True
        assert "resetToken" not in res_staging.json()

        # 4. Environment is 'test' / other -> resetToken must NEVER be returned
        monkeypatch.setattr(settings, "ENVIRONMENT", "test")
        res_test = client.post("/api/auth/forgot-password", json={"email": "geologist@example.com"})
        assert res_test.status_code == 200
        assert res_test.json().get("success") is True
        assert "resetToken" not in res_test.json()
    finally:
        app.dependency_overrides.clear()


def test_change4_require_id_match_when_finding_user():
    """Change 4: Require an id match when finding the user.
    get_current_user_optional should not fall back to email lookup when token's user id is not found.
    """
    mock_db = MagicMock()

    # Suppose a token was issued to user_id = 'deleted-user-id' with email 'reused@example.com'
    session_data = {
        "id": "deleted-user-id",
        "email": "reused@example.com",
    }

    mock_db.query.return_value.filter.return_value.first.return_value = None

    scope = {
        "type": "http",
        "headers": [(b"cookie", b"wellqc_session=mock_encrypted_token")],
    }
    request = Request(scope)

    with patch("backend.app.core.dependencies.read_session_token", return_value=session_data):
        user = get_current_user_optional(request=request, bearer_creds=None, db=mock_db)
        assert user is None

        # Verify query was called with User
        mock_db.query.assert_called_with(User)
        # Verify it filtered only by User.id, never by User.email
        filter_calls = mock_db.query.return_value.filter.call_args_list
        assert len(filter_calls) == 1
        # Check that it did not issue an email query


def test_change5_no_in_memory_alias_fallback():
    """Change 5: Remove in-memory alias fallback.
    - get_custom_aliases() returns []
    - set_custom_aliases(...) is a no-op
    - standardise_mnemonic with custom_list=None does not use any global in-memory custom aliases
    """
    # Verify get_custom_aliases() returns empty list
    assert get_custom_aliases() == []

    # Verify set_custom_aliases does not persist
    set_custom_aliases([{"pattern": "MYCURVE", "standard": "GR"}])
    assert get_custom_aliases() == []

    # Verify standardise_mnemonic with custom_list=None does not match as custom alias
    res_none = standardise_mnemonic("MYCURVE", custom_list=None)
    assert res_none.confidence < 0.5  # UNKNOWN fallback confidence is 0.2

    # But when explicitly passed in custom_list (e.g. from user DB query), it resolves as custom alias
    custom_entry = CustomAliasEntry(
        id="alias-1",
        alias="MYCURVE",
        standardMnemonic="GR",
        addedBy="Petrophysicist",
        addedAt="2026-10-26T12:00:00Z",
    )
    res_custom = standardise_mnemonic("MYCURVE", custom_list=[custom_entry])
    assert res_custom.standardMnemonic == "GR"
    assert res_custom.matchType == "CUSTOM"
    assert res_custom.confidence == 0.98

    # Verify add, edit, remove work without modifying any in-memory global state
    add_res = add_custom_alias("GR", "GR_TEST", custom_list=[])
    assert add_res.success is True
    assert get_custom_aliases() == []


def test_change2_clean_user_dependencies_no_activity_log_update():
    """Change 2: Remove redundant update on user delete in admin.py.
    Ensure _clean_user_dependencies does not execute an UPDATE 'ActivityLog' SET 'userId' = NULL query.
    """
    from backend.app.api.admin import _clean_user_dependencies

    mock_db = MagicMock()
    # Execute should NOT be called with an UPDATE ActivityLog query
    _clean_user_dependencies(mock_db, ["user-to-delete-123"])

    for call_item in mock_db.execute.call_args_list:
        query_str = str(call_item[0][0])
        assert "ActivityLog" not in query_str, f"Found forbidden ActivityLog query: {query_str}"
