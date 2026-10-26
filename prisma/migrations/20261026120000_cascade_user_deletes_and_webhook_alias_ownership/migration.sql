-- DropForeignKey
ALTER TABLE "Well" DROP CONSTRAINT "Well_ownerId_fkey";

-- DropForeignKey
ALTER TABLE "LASFile" DROP CONSTRAINT "LASFile_uploadedById_fkey";

-- DropForeignKey
ALTER TABLE "LASFile" DROP CONSTRAINT "LASFile_ownerId_fkey";

-- DropForeignKey
ALTER TABLE "Curve" DROP CONSTRAINT "Curve_ownerId_fkey";

-- DropForeignKey
ALTER TABLE "QualityReport" DROP CONSTRAINT "QualityReport_ownerId_fkey";

-- DropForeignKey
ALTER TABLE "Anomaly" DROP CONSTRAINT "Anomaly_ownerId_fkey";

-- AlterTable
ALTER TABLE "Webhook" ADD COLUMN     "userId" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "CustomAlias" ALTER COLUMN "userId" SET NOT NULL;

-- CreateIndex
CREATE INDEX "Webhook_userId_idx" ON "Webhook"("userId");

-- AddForeignKey
ALTER TABLE "Well" ADD CONSTRAINT "Well_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LASFile" ADD CONSTRAINT "LASFile_uploadedById_fkey" FOREIGN KEY ("uploadedById") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "LASFile" ADD CONSTRAINT "LASFile_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Curve" ADD CONSTRAINT "Curve_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "QualityReport" ADD CONSTRAINT "QualityReport_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Anomaly" ADD CONSTRAINT "Anomaly_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Webhook" ADD CONSTRAINT "Webhook_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CustomAlias" ADD CONSTRAINT "CustomAlias_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;
