-- Row-level security, Sprint 5 Step 4, pull request B.
-- Run by CI as neondb_owner (the table owner). Do NOT use FORCE ROW LEVEL SECURITY:
-- migrations run as the owner and must keep working.
--
-- The application sets two transaction-local values (database.py, pull request A):
--   app.user_id  text, '' = no user (default-deny)
--   app.is_admin 'true' or 'false'
-- Admin sees every row. Rows whose owner column is NULL are visible to admins only.
-- Referential actions (the cascade deletes from the Oct 26 migration) bypass RLS.

CREATE OR REPLACE FUNCTION public.app_user_id() RETURNS text
LANGUAGE sql STABLE AS $$ SELECT nullif(current_setting('app.user_id', true), '') $$;

CREATE OR REPLACE FUNCTION public.app_is_admin() RETURNS boolean
LANGUAGE sql STABLE AS $$ SELECT coalesce(current_setting('app.is_admin', true) = 'true', false) $$;

-- Guarded so the migration also runs where the wellqc_api role does not exist.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wellqc_api') THEN
    GRANT EXECUTE ON FUNCTION public.app_user_id(), public.app_is_admin() TO wellqc_api;
  END IF;
END
$$;

-- Well (owner column "ownerId")
ALTER TABLE "Well" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS well_isolation ON "Well";
CREATE POLICY well_isolation ON "Well"
  USING      ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()));

-- LASFile (owner column "ownerId")
ALTER TABLE "LASFile" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS lasfile_isolation ON "LASFile";
CREATE POLICY lasfile_isolation ON "LASFile"
  USING      ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()));

-- Curve (owner column "ownerId")
ALTER TABLE "Curve" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS curve_isolation ON "Curve";
CREATE POLICY curve_isolation ON "Curve"
  USING      ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()));

-- QualityReport (owner column "ownerId")
ALTER TABLE "QualityReport" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS qualityreport_isolation ON "QualityReport";
CREATE POLICY qualityreport_isolation ON "QualityReport"
  USING      ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()));

-- Anomaly (owner column "ownerId")
ALTER TABLE "Anomaly" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS anomaly_isolation ON "Anomaly";
CREATE POLICY anomaly_isolation ON "Anomaly"
  USING      ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "ownerId" = (SELECT app_user_id()));

-- CustomAlias (owner column "userId")
ALTER TABLE "CustomAlias" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS customalias_isolation ON "CustomAlias";
CREATE POLICY customalias_isolation ON "CustomAlias"
  USING      ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()));

-- Webhook (owner column "userId")
ALTER TABLE "Webhook" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS webhook_isolation ON "Webhook";
CREATE POLICY webhook_isolation ON "Webhook"
  USING      ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()));

-- APIToken (owner column "userId")
ALTER TABLE "APIToken" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS apitoken_isolation ON "APIToken";
CREATE POLICY apitoken_isolation ON "APIToken"
  USING      ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()))
  WITH CHECK ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()));

-- ActivityLog (owner decision Q3 B): inserts always allowed (auth.py writes rows before any
-- context exists); users read their own rows, admins read all. There is deliberately no
-- UPDATE or DELETE policy, so the application role cannot change or purge log rows.
-- Note: INSERT ... RETURNING also needs the SELECT policy to pass for the new row (test T7b).
ALTER TABLE "ActivityLog" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS activitylog_select ON "ActivityLog";
DROP POLICY IF EXISTS activitylog_insert ON "ActivityLog";
CREATE POLICY activitylog_select ON "ActivityLog" FOR SELECT
  USING ((SELECT app_is_admin()) OR "userId" = (SELECT app_user_id()));
CREATE POLICY activitylog_insert ON "ActivityLog" FOR INSERT
  WITH CHECK (true);
