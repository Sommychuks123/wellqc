import time
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

SAMPLE_LAS = """~Version Information
VERS.   2.0 : CWLS LOG ASCII STANDARD - VERSION 2.0
WRAP.    NO : ONE LINE PER DEPTH STEP
~Well Information
#MNEM.UNIT       DATA                       DESCRIPTION
#----.----       ------------------------- ---------------------------------
STRT .M          1000.0000                 : START DEPTH
STOP .M          1005.0000                 : STOP DEPTH
STEP .M          1.0000                    : STEP
NULL .           -999.2500                 : NULL VALUE
WELL .           ANALYTICS-TEST-WELL       : WELL NAME
COMP .           CHEVRON NIGERIA           : COMPANY
FLD  .           AGBAMI DEEP               : FIELD
LOC  .           NIGER DELTA BASIN         : LOCATION
~Curve Information
#MNEM.UNIT       API CODES                 DESCRIPTION
#----.----       ------------------------- ---------------------------------
DEPT .M                                    : 1  DEPTH
GR   .GAPI                                 : 2  GAMMA RAY
RHOB .G/CC                                 : 3  BULK DENSITY
~A Depth         GR       RHOB
 1000.0000       45.20    2.35
 1001.0000       52.10    2.40
 1002.0000       -999.25  2.38
 1003.0000       60.40    -999.25
 1004.0000       58.90    2.42
 1005.0000       61.00    2.45
"""

def _get_auth_client(role="PETROPHYSICIST"):
    client = TestClient(app)
    ts = int(time.time() * 1000)
    email = f"analytics_{ts}@wellqc.com"
    pwd = "Password123!"
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "name": "Analytics Test User",
            "email": email,
            "password": pwd,
            "role": role,
            "acceptedNda": True,
        },
    )
    assert reg_resp.status_code == 201
    verification_token = reg_resp.json().get("verificationToken")
    if verification_token:
        verify_resp = client.get(f"/api/auth/verify-email?token={verification_token}")
        assert verify_resp.status_code == 200

    login_resp = client.post(
        "/api/auth/login",
        json={"email": email, "password": pwd},
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("token")
    return client, login_resp.json(), token

def test_analytics_requires_auth():
    client = TestClient(app)
    resp = client.get("/api/analytics")
    assert resp.status_code == 401

def test_analytics_empty_for_new_user():
    client, _, token = _get_auth_client()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/analytics", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert data["summary"]["totalWells"] == 0
    assert data["summary"]["totalFiles"] == 0
    assert data["operatorScores"] == []
    assert data["anomalyDistribution"] == []
    assert data["wells"] == []

def test_analytics_with_uploaded_well():
    client, _, token = _get_auth_client()
    headers = {"Authorization": f"Bearer {token}"}

    # Upload a LAS file
    upload_resp = client.post(
        "/api/las",
        json={"fileName": "analytics_test.las", "content": SAMPLE_LAS},
        headers=headers,
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert "well" in upload_data

    # Now fetch analytics
    analytics_resp = client.get("/api/analytics", headers=headers)
    assert analytics_resp.status_code == 200
    data = analytics_resp.json()

    # Verify summary telemetry
    assert "summary" in data
    assert data["summary"]["totalWells"] >= 1
    assert data["summary"]["totalFiles"] >= 1
    assert data["summary"]["avgQualityScore"] > 0
    assert "topOperator" in data["summary"]
    assert "topBasin" in data["summary"]

    # Verify operator scores
    assert len(data["operatorScores"]) >= 1
    op_entry = data["operatorScores"][0]
    assert "operator" in op_entry
    assert "score" in op_entry
    assert "files" in op_entry
    assert op_entry["files"] >= 1

    # Verify basin scores
    assert "basinScores" in data
    assert len(data["basinScores"]) >= 1
    basin_entry = data["basinScores"][0]
    assert "basin" in basin_entry
    assert "score" in basin_entry

    # Verify anomaly distribution
    assert "anomalyDistribution" in data
    if len(data["anomalyDistribution"]) > 0:
        anom = data["anomalyDistribution"][0]
        assert "name" in anom
        assert "value" in anom
        assert "color" in anom

    # Verify wells list
    assert "wells" in data
    assert len(data["wells"]) >= 1
    well = data["wells"][0]
    assert "id" in well
    assert "name" in well
    assert "operator" in well
    assert "qualityScore" in well

    # Test filtering by operator
    op_name = op_entry["operator"]
    filtered_resp = client.get(f"/api/analytics?operator={op_name}", headers=headers)
    assert filtered_resp.status_code == 200
    assert len(filtered_resp.json()["wells"]) >= 1

    # Test filtering by non-matching operator
    non_match_resp = client.get("/api/analytics?operator=NonExistentCorp", headers=headers)
    assert non_match_resp.status_code == 200
    assert len(non_match_resp.json()["wells"]) == 0
