"""
Row-level security policy tests (Sprint 5, Step 4, pull request B).

DRAFT: not run. Run on DEV only, as the non-owner role wellqc_api:

    PY_TEST_DATABASE_URL=<dev wellqc_api string, pooled host>  pytest backend/tests/test_rls_policies.py -v

Optional: PY_OWNER_DATABASE_URL (dev neondb_owner) lets teardown purge the ActivityLog rows these tests
create, because the application role has no DELETE policy on that table by design.

Covers T1 to T4, T7 (7a, 7b, 7c), T8, T9 and the null-owner admin-only case. T0, T5 and T6 are in pull
request A; the guard below repeats T0 so this file is safe to run alone (drop it if you prefer).
T10 is the existing suite run with the policies in place.
"""
import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

DB_URL = os.environ.get("PY_TEST_DATABASE_URL")
OWNER_URL = os.environ.get("PY_OWNER_DATABASE_URL")

pytestmark = pytest.mark.skipif(not DB_URL, reason="PY_TEST_DATABASE_URL not set")

OWNER_COL = {
    "Well": "ownerId", "LASFile": "ownerId", "Curve": "ownerId", "QualityReport": "ownerId",
    "Anomaly": "ownerId", "CustomAlias": "userId", "Webhook": "userId", "APIToken": "userId",
}
RLS_TABLES = list(OWNER_COL) + ["ActivityLog"]
NO_RLS_TABLES = ["User", "SystemSetting", "Field", "Operator"]
EXPECTED_POLICIES = {t: [t.lower() + "_isolation"] for t in OWNER_COL}
EXPECTED_POLICIES["ActivityLog"] = ["activitylog_insert", "activitylog_select"]

RLS_VIOLATION = "42501"  # insufficient_privilege: "new row violates row-level security policy"

_SET_CTX = text("select set_config('app.user_id', :u, true), set_config('app.is_admin', :a, true)")


def set_ctx(conn, user_id="", admin=False):
    conn.execute(_SET_CTX, {"u": user_id, "a": "true" if admin else "false"})


def uid():
    return str(uuid.uuid4())


# --------------------------------------------------------------------------- fixtures
@pytest.fixture(scope="module")
def engine():
    eng = create_engine(DB_URL, pool_pre_ping=True)
    yield eng
    eng.dispose()


@pytest.fixture(scope="module", autouse=True)
def rls_guard(engine):
    """T0: refuse to run as a role that bypasses RLS or owns the tables (a wrong secret must never pass)."""
    with engine.connect() as c:
        row = c.execute(text(
            "select current_user, r.rolbypassrls, r.rolsuper, "
            "(select count(*) from pg_class where relname in ('Well','LASFile','Curve','QualityReport',"
            "'Anomaly','CustomAlias','Webhook','APIToken','ActivityLog') and relkind='r' "
            "and pg_get_userbyid(relowner) = current_user) "
            "from pg_roles r where r.rolname = current_user")).one()
    name, bypass, superuser, owned = row
    if bypass or superuser or owned:
        pytest.exit(f"T0: {name} bypasses RLS or owns policy tables (bypass={bypass}, super={superuser}, "
                    f"owned={owned}); wrong database secret, aborting.", returncode=2)


@pytest.fixture(scope="module")
def fx(engine):
    """Run-scoped shared rows (Field and Operator have no RLS) and three users."""
    run = uuid.uuid4().hex[:8]
    f = {"run": run, "field": f"rlstest-field-{run}", "operator": f"rlstest-op-{run}",
         "A": uid(), "B": uid(), "ADMIN": uid(), "C": uid()}
    with engine.begin() as c:
        c.execute(text('insert into "Field"(id,name,basin,country) values (:i,:n,\'rlstest\',\'NG\')'),
                  {"i": uid(), "n": f["field"]})
        c.execute(text('insert into "Operator"(id,name) values (:i,:n)'), {"i": uid(), "n": f["operator"]})
        for key, role in (("A", "USER"), ("B", "USER"), ("ADMIN", "ADMIN"), ("C", "USER")):
            c.execute(text(
                'insert into "User"(id,email,name,"passwordHash",role,tier,"freeChecksUsed",'
                '"isEmailVerified","createdAt","updatedAt") '
                "values (:i,:e,:n,'x',:r,'FREE',0,true,now(),now())"),
                {"i": f[key], "e": f"rlstest-{key.lower()}-{run}@example.invalid", "n": f"rlstest {key}", "r": role})
    yield f
    # Teardown: deleting the users cascades to their data (Q4 A); then the shared rows.
    try:
        with engine.begin() as c:
            for key in ("A", "B", "ADMIN", "C"):
                c.execute(text('delete from "User" where id = :i'), {"i": f[key]})
            c.execute(text('delete from "Field" where name = :n'), {"n": f["field"]})
            c.execute(text('delete from "Operator" where name = :n'), {"n": f["operator"]})
    except Exception as e:  # pragma: no cover
        print(f"WARNING: teardown of rlstest rows failed, clean up manually (run {run}): {e}")
    if OWNER_URL:
        owner_eng = create_engine(OWNER_URL)
        with owner_eng.begin() as c:
            c.execute(text('delete from "ActivityLog" where details like :p'), {"p": f"rlstest-{run}%"})
        owner_eng.dispose()


# --------------------------------------------------------------------------- row builders
def insert_row(conn, table, owner, fx, parents=None):
    """Insert one row of `table` owned by `owner` (None allowed for the five ownerId tables)."""
    p = parents or {}
    i = uid()
    run = fx["run"]
    if table == "Well":
        conn.execute(text(
            'insert into "Well"(id,"apiNo",name,"operatorName","fieldName",basin,country,latitude,longitude,'
            '"ownerId","updatedAt") values (:i,:api,:n,:op,:f,\'rlstest\',\'NG\',0,0,:o,now())'),
            {"i": i, "api": f"rlstest-{run}-{i[:8]}", "n": "rlstest well", "op": fx["operator"],
             "f": fx["field"], "o": owner})
    elif table == "LASFile":
        conn.execute(text(
            'insert into "LASFile"(id,"wellId","originalName","fileSizeKb","startDepth","stopDepth","stepDepth",'
            '"rawHeader","ownerId") values (:i,:w,\'t.las\',1,0,1,0.5,\'h\',:o)'),
            {"i": i, "w": p["Well"], "o": owner})
    elif table == "Curve":
        conn.execute(text(
            'insert into "Curve"(id,"lasFileId","originalMnemonic","ownerId") values (:i,:l,\'GR\',:o)'),
            {"i": i, "l": p["LASFile"], "o": owner})
    elif table == "QualityReport":
        conn.execute(text(
            'insert into "QualityReport"(id,"wellId","lasFileId","ownerId") values (:i,:w,:l,:o)'),
            {"i": i, "w": p["Well"], "l": p["LASFile"], "o": owner})
    elif table == "Anomaly":
        conn.execute(text(
            'insert into "Anomaly"(id,"qualityReportId","curveMnemonic","depthStart","depthEnd","anomalyType",'
            'severity,description,"suggestedCorrection","ownerId") '
            "values (:i,:q,'GR',0,1,'FLATLINE','INFO','d','c',:o)"),
            {"i": i, "q": p["QualityReport"], "o": owner})
    elif table == "CustomAlias":
        conn.execute(text(
            'insert into "CustomAlias"(id,alias,"standardMnemonic","addedBy","userId") '
            "values (:i,:a,'GR','rlstest',:o)"), {"i": i, "a": f"rlstest-{run}-{i[:8]}", "o": owner})
    elif table == "Webhook":
        conn.execute(text(
            'insert into "Webhook"(id,name,url,secret,events,"userId") '
            "values (:i,'w','https://example.invalid','s','[]',:o)"), {"i": i, "o": owner})
    elif table == "APIToken":
        conn.execute(text('insert into "APIToken"(id,name,token,"userId") values (:i,\'t\',:t,:o)'),
                     {"i": i, "t": f"rlstest-{run}-{i}", "o": owner})
    else:
        raise ValueError(table)
    return i


def seed_tree(engine, owner, fx):
    """Insert one row in every owner table for `owner`, under that owner's own context."""
    ids = {}
    with engine.begin() as c:
        set_ctx(c, owner)
        for t in ("Well", "LASFile", "Curve", "QualityReport", "Anomaly", "CustomAlias", "Webhook", "APIToken"):
            ids[t] = insert_row(c, t, owner, fx, ids)
    return ids


@pytest.fixture(scope="module")
def trees(engine, fx):
    return {"A": seed_tree(engine, fx["A"], fx), "B": seed_tree(engine, fx["B"], fx)}


def count_ids(conn, table, ids):
    return conn.execute(text(f'select count(*) from "{table}" where id = any(:ids)'),
                        {"ids": list(ids)}).scalar()


# --------------------------------------------------------------------------- T1 to T3
@pytest.mark.parametrize("table", list(OWNER_COL))
def test_t1_user_sees_only_own_rows(engine, fx, trees, table):
    with engine.begin() as c:
        set_ctx(c, fx["A"])
        assert count_ids(c, table, [trees["A"][table]]) == 1
        assert count_ids(c, table, [trees["B"][table]]) == 0


@pytest.mark.parametrize("table", RLS_TABLES)
def test_t2_no_context_sees_nothing(engine, fx, trees, table):
    with engine.begin() as c:  # never calls set_ctx
        assert c.execute(text(f'select count(*) from "{table}"')).scalar() == 0
    with engine.begin() as c:  # explicit empty context is the same as none
        set_ctx(c, "", False)
        assert c.execute(text(f'select count(*) from "{table}"')).scalar() == 0


@pytest.mark.parametrize("table", list(OWNER_COL))
def test_t3_admin_sees_all(engine, fx, trees, table):
    with engine.begin() as c:
        set_ctx(c, fx["ADMIN"], admin=True)
        assert count_ids(c, table, [trees["A"][table], trees["B"][table]]) == 2


# --------------------------------------------------------------------------- T4
@pytest.mark.parametrize("table", list(OWNER_COL))
def test_t4_insert_for_another_owner_is_rejected(engine, fx, trees, table):
    with pytest.raises(DBAPIError) as e:
        with engine.begin() as c:
            set_ctx(c, fx["A"])
            insert_row(c, table, fx["B"], fx, trees["A"])  # A acting, row says B
    assert e.value.orig.pgcode == RLS_VIOLATION


@pytest.mark.parametrize("table", list(OWNER_COL))
def test_t4_no_context_insert_is_rejected(engine, fx, trees, table):
    with pytest.raises(DBAPIError) as e:
        with engine.begin() as c:
            insert_row(c, table, fx["A"], fx, trees["A"])
    assert e.value.orig.pgcode == RLS_VIOLATION


def test_t4_user_cannot_hand_a_row_to_someone_else(engine, fx, trees):
    """UPDATE that changes the owner is stopped by WITH CHECK."""
    with pytest.raises(DBAPIError) as e:
        with engine.begin() as c:
            set_ctx(c, fx["A"])
            c.execute(text('update "Well" set "ownerId" = :b where id = :w'),
                      {"b": fx["B"], "w": trees["A"]["Well"]})
    assert e.value.orig.pgcode == RLS_VIOLATION


def test_t4_user_cannot_touch_another_users_row(engine, fx, trees):
    """UPDATE and DELETE on someone else's row match zero rows, they do not error."""
    with engine.begin() as c:
        set_ctx(c, fx["A"])
        assert c.execute(text('update "Well" set name = \'hijack\' where id = :w'),
                         {"w": trees["B"]["Well"]}).rowcount == 0
        assert c.execute(text('delete from "Well" where id = :w'), {"w": trees["B"]["Well"]}).rowcount == 0


# --------------------------------------------------------------------------- null-owner case
def test_null_owner_row_is_admin_only(engine, fx):
    """A row with a NULL owner (the five Primary leftovers looked like this) is visible to admins only."""
    with engine.begin() as c:
        set_ctx(c, fx["ADMIN"], admin=True)
        wid = insert_row(c, "Well", None, fx)
    try:
        with engine.begin() as c:
            set_ctx(c, fx["A"])
            assert count_ids(c, "Well", [wid]) == 0
        with engine.begin() as c:
            assert count_ids(c, "Well", [wid]) == 0
        with engine.begin() as c:
            set_ctx(c, fx["ADMIN"], admin=True)
            assert count_ids(c, "Well", [wid]) == 1
        with pytest.raises(DBAPIError) as e:  # a non-admin cannot create one either
            with engine.begin() as c:
                set_ctx(c, fx["A"])
                insert_row(c, "Well", None, fx)
        assert e.value.orig.pgcode == RLS_VIOLATION
    finally:
        with engine.begin() as c:
            set_ctx(c, fx["ADMIN"], admin=True)
            c.execute(text('delete from "Well" where id = :w'), {"w": wid})


# --------------------------------------------------------------------------- T7 ActivityLog
def _log_insert(c, fx, user_id, returning=False):
    sql = ('insert into "ActivityLog"(id,"userId",action,details) values (:i,:u,\'LOGIN\',:d)'
           + (" returning id" if returning else ""))
    return c.execute(text(sql), {"i": uid(), "u": user_id, "d": f"rlstest-{fx['run']} {uid()}"})


def test_t7a_insert_without_context_succeeds(engine, fx):
    """auth.py writes rows before any context exists, with or without a userId."""
    with engine.begin() as c:
        _log_insert(c, fx, None)
    with engine.begin() as c:
        _log_insert(c, fx, fx["A"])


@pytest.mark.xfail(strict=True, raises=DBAPIError,
                   reason="Postgres also applies the SELECT policy to INSERT ... RETURNING. Expected to "
                          "fail while the app inserts activity-log rows with RETURNING and no context. "
                          "strict: if this starts passing, the behaviour changed and must be re-decided.")
def test_t7b_insert_returning_without_context(engine, fx):
    with engine.begin() as c:
        assert _log_insert(c, fx, fx["A"], returning=True).scalar() is not None


def test_t7b_insert_returning_with_matching_context(engine, fx):
    """RETURNING works when the caller's context matches the row's userId (the fix if 7b fails)."""
    with engine.begin() as c:
        set_ctx(c, fx["A"])
        assert _log_insert(c, fx, fx["A"], returning=True).scalar() is not None


def test_t7c_users_read_own_log_rows_admin_reads_all(engine, fx):
    with engine.begin() as c:
        set_ctx(c, fx["B"])
        _log_insert(c, fx, fx["B"])
        _log_insert(c, fx, None)  # a null-userId row
    pattern = f"rlstest-{fx['run']}%"
    q = text('select count(*) from "ActivityLog" where details like :p and "userId" is not distinct from :u')
    with engine.begin() as c:
        set_ctx(c, fx["B"])
        assert c.execute(q, {"p": pattern, "u": fx["B"]}).scalar() >= 1
        assert c.execute(q, {"p": pattern, "u": fx["A"]}).scalar() == 0  # A's rows from 7a are hidden
        assert c.execute(q, {"p": pattern, "u": None}).scalar() == 0     # null-userId rows are hidden
    with engine.begin() as c:
        set_ctx(c, fx["ADMIN"], admin=True)
        assert c.execute(q, {"p": pattern, "u": fx["A"]}).scalar() >= 1
        assert c.execute(q, {"p": pattern, "u": None}).scalar() >= 1


def test_t7d_application_role_cannot_update_or_delete_log_rows(engine, fx):
    """There is no UPDATE or DELETE policy, so both match zero rows (audit trail stays intact)."""
    with engine.begin() as c:
        set_ctx(c, fx["ADMIN"], admin=True)
        assert c.execute(text('update "ActivityLog" set details = details where details like :p'),
                         {"p": f"rlstest-{fx['run']}%"}).rowcount == 0
        assert c.execute(text('delete from "ActivityLog" where details like :p'),
                         {"p": f"rlstest-{fx['run']}%"}).rowcount == 0


# --------------------------------------------------------------------------- T8
def test_t8_deleting_a_user_deletes_their_data(engine, fx):
    ids = seed_tree(engine, fx["C"], fx)
    with engine.begin() as c:
        set_ctx(c, fx["ADMIN"], admin=True)
        for t in OWNER_COL:
            assert count_ids(c, t, [ids[t]]) == 1, t
        c.execute(text('delete from "User" where id = :u'), {"u": fx["C"]})
    with engine.begin() as c:
        set_ctx(c, fx["ADMIN"], admin=True)
        for t in OWNER_COL:
            assert count_ids(c, t, [ids[t]]) == 0, t


# --------------------------------------------------------------------------- T9
def test_t9_rls_flags_and_policies(engine):
    with engine.connect() as c:
        flags = dict(c.execute(text(
            "select relname, relrowsecurity from pg_class where relkind = 'r' and relnamespace = 'public'::regnamespace"
        )).all())
        force = dict(c.execute(text(
            "select relname, relforcerowsecurity from pg_class where relkind = 'r' and relnamespace = 'public'::regnamespace"
        )).all())
        pols = {}
        for tbl, name in c.execute(text("select tablename, policyname from pg_policies where schemaname = 'public'")):
            pols.setdefault(tbl, []).append(name)
    for t in RLS_TABLES:
        assert flags.get(t) is True, f"RLS not enabled on {t}"
        assert force.get(t) is False, f"FORCE RLS must stay off on {t}"
        assert sorted(pols.get(t, [])) == sorted(EXPECTED_POLICIES[t]), f"policies on {t}: {pols.get(t)}"
    for t in NO_RLS_TABLES:
        assert flags.get(t) is False, f"RLS unexpectedly on for {t} (v1 leaves it off)"
