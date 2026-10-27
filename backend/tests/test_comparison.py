import pytest
import numpy as np
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.comparison import (
    compare_two_wells,
    _compute_lag_shift,
    _clean_curve_series,
    _estimate_formations,
)
from backend.app.models.models import User, Well, LASFile, Curve
from backend.app.core.database import SessionLocal
from backend.app.core.security import create_session_token

client = TestClient(app)


def test_clean_curve_series():
    depth = np.array([1000.0, 1001.0, 1002.0, 1003.0, 1004.0])
    vals = np.array([50.0, -999.25, np.nan, 75.0, np.inf])
    cd, cv = _clean_curve_series(depth, vals)
    assert len(cd) == 2
    assert list(cd) == [1000.0, 1003.0]
    assert list(cv) == [50.0, 75.0]


def test_compute_lag_shift():
    # Signal with known sinusoidal shape
    x = np.linspace(0, 4 * np.pi, 100)
    signal = np.sin(x)
    # Shifted signal by 5 steps
    grid_step = 0.5
    s_a = signal
    s_b = np.roll(signal, 5)
    best_lag_depth, max_corr = _compute_lag_shift(grid_step, s_a, s_b, max_steps=10)
    assert max_corr > 0.95
    assert abs(abs(best_lag_depth) - (5 * grid_step)) < 0.01


def test_estimate_formations():
    depth = np.linspace(2000, 6000, 100)
    gr = np.linspace(40, 120, 100)
    markers = _estimate_formations(depth, {"GR": gr})
    assert "Benin" in markers
    assert "Agbada" in markers
    assert "Akata" in markers
    assert markers["Benin"] == 2000.0
    assert markers["Agbada"] is not None
    assert markers["Akata"] is not None
    assert markers["Agbada"] < markers["Akata"]


def test_compare_two_wells_identical():
    depth = list(np.linspace(1000, 2000, 200))
    # Synthetic gamma ray and resistivity
    gr = list(50 + 25 * np.sin(np.linspace(0, 10, 200)))
    rt = list(10 + 5 * np.cos(np.linspace(0, 10, 200)))

    data_a = {
        "depth": depth,
        "curves": {"GR": gr, "RT": rt},
    }
    data_b = {
        "depth": depth,
        "curves": {"GR": gr, "RT": rt},
    }

    res = compare_two_wells(
        well_a_id="well-1",
        well_a_name="Well-01",
        curves_data_a=data_a,
        well_b_id="well-2",
        well_b_name="Well-02",
        curves_data_b=data_b,
        depth_unit="FT",
    )

    assert res.composite_correlation_score >= 95.0
    assert res.overall_match_grade == "EXCELLENT_MATCH"
    assert "GR" in res.common_curves
    assert "RT" in res.common_curves
    assert len(res.curve_correlations) == 2

    gr_stat = next(c for c in res.curve_correlations if c.mnemonic == "GR")
    assert gr_stat.pearson_r > 0.98
    assert gr_stat.stratigraphic_continuity == "HIGH"
    assert gr_stat.rmsd < 0.1


def test_compare_two_wells_with_depth_offset():
    # Well A logged from 2000 to 4000
    depth_a = list(np.linspace(2000, 4000, 200))
    # Well B logged from 2500 to 4500 (overlap is 2500 to 4000)
    depth_b = list(np.linspace(2500, 4500, 200))

    data_a = {
        "depth": depth_a,
        "curves": {"GR": list(np.random.normal(60, 10, 200))},
    }
    data_b = {
        "depth": depth_b,
        "curves": {"GR": list(np.random.normal(60, 10, 200))},
    }

    res = compare_two_wells(
        well_a_id="well-a",
        well_a_name="Well A",
        curves_data_a=data_a,
        well_b_id="well-b",
        well_b_name="Well B",
        curves_data_b=data_b,
    )

    assert res.overlap_start_depth == 2500.0
    assert res.overlap_stop_depth == 4000.0
    assert res.overlap_span == 1500.0


def test_compare_endpoint_validation():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "analyst@wellqc.com").first()
        if not user:
            import uuid
            user = User(
                id=str(uuid.uuid4()),
                email="analyst@wellqc.com",
                name="QC Analyst",
                passwordHash="test_hash_secret_123",
                role="USER",
                department="Petrophysics",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        token = create_session_token({
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
        })
    finally:
        db.close()

    headers = {"Authorization": f"Bearer {token}"}
    client.cookies.set("wellqc_session", token)

    # Empty payload should fail validation
    res = client.post("/api/wells/compare", json={}, headers=headers)
    assert res.status_code == 422

    # Malicious injection attempt in ID should be caught
    res_mal = client.post(
        "/api/wells/compare",
        json={"primary_well_id": "'; DROP TABLE wells; --", "offset_well_id": "valid-id"},
        headers=headers,
    )
    assert res_mal.status_code in [400, 422]

    # Non-existent wells should return 404
    res_404 = client.post(
        "/api/wells/compare",
        json={"primary_well_id": "non-existent-1", "offset_well_id": "non-existent-2"},
        headers=headers,
    )
    assert res_404.status_code == 404
