-- Rollback for 20261027130000_enable_row_level_security.
-- Run as neondb_owner. Policies and the two functions can stay; with RLS disabled they do nothing,
-- and the application code from pull request A is harmless without RLS.
ALTER TABLE "Well" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "LASFile" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "Curve" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "QualityReport" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "Anomaly" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "CustomAlias" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "Webhook" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "APIToken" DISABLE ROW LEVEL SECURITY;
ALTER TABLE "ActivityLog" DISABLE ROW LEVEL SECURITY;

-- Check afterwards: every row should read false.
-- select relname, relrowsecurity from pg_class
-- where relname in ('Well','LASFile','Curve','QualityReport','Anomaly','CustomAlias','Webhook','APIToken','ActivityLog')
--   and relkind = 'r' order by 1;
