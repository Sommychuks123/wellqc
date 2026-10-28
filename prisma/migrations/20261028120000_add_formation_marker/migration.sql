CREATE TABLE IF NOT EXISTS "FormationMarker" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "wellId" TEXT NOT NULL REFERENCES "Well"("id") ON DELETE CASCADE,
    "formationName" TEXT NOT NULL,
    "topDepth" DOUBLE PRECISION NOT NULL,
    "bottomDepth" DOUBLE PRECISION,
    "source" TEXT NOT NULL DEFAULT 'INTERPRETER',
    "pickedBy" TEXT,
    "notes" TEXT,
    "ownerId" TEXT REFERENCES "User"("id") ON DELETE CASCADE,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT "FormationMarker_wellId_formationName_key" UNIQUE ("wellId", "formationName")
);
CREATE INDEX IF NOT EXISTS "FormationMarker_wellId_idx" ON "FormationMarker"("wellId");

DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'wellqc_api') THEN
    GRANT SELECT, INSERT, UPDATE, DELETE ON "FormationMarker" TO wellqc_api;
  END IF;
END $$;

-- FormationMarker (visible only when its well is visible; Well's own policy decides)
ALTER TABLE "FormationMarker" ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS formationmarker_isolation ON "FormationMarker";
CREATE POLICY formationmarker_isolation ON "FormationMarker"
  USING      (EXISTS (SELECT 1 FROM "Well" w WHERE w."id" = "FormationMarker"."wellId"))
  WITH CHECK (EXISTS (SELECT 1 FROM "Well" w WHERE w."id" = "FormationMarker"."wellId"));
