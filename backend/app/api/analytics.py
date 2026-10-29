from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, desc
from backend.app.core.database import get_db
from backend.app.core.dependencies import get_current_user
from backend.app.core.security import normalize_role
from backend.app.models.models import Anomaly, QualityReport, User, Well

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

ANOMALY_COLORS = {
    "IMPOSSIBLE_VALUE": "#ef4444",        # Red
    "EXTREME_SPIKE": "#f59e0b",           # Amber
    "FLATLINE": "#06b6d4",                # Cyan
    "DEPTH_GAP": "#3b82f6",               # Blue
    "NULL_CLUSTER": "#ec4899",            # Pink
    "NULL_DEPTH": "#e11d48",              # Rose
    "DUPLICATE_DEPTH": "#14b8a6",         # Teal
    "CYCLE_SKIP": "#a855f7",              # Purple
    "UNIT_MISMATCH": "#8b5cf6",           # Violet
    "UNIT_INFERRED": "#6366f1",           # Indigo
    "NON_STANDARD_MNEMONIC": "#f97316",   # Orange
    "OUT_OF_TYPICAL_RANGE": "#eab308",    # Yellow
    "DUPLICATE_CURVE": "#10b981",         # Emerald
    "MISSING_CORE_CURVE": "#d946ef",      # Fuchsia
}

SEVERITY_COLORS = {
    "CRITICAL": "#ef4444",
    "HIGH": "#f97316",
    "MEDIUM": "#f59e0b",
    "WARNING": "#eab308",
    "LOW": "#3b82f6",
    "INFO": "#06b6d4",
}

GRADE_COLORS = {
    "EXCELLENT": "#10b981",
    "GOOD": "#06b6d4",
    "POOR": "#f59e0b",
    "CRITICAL": "#ef4444",
}


@router.get("")
def get_analytics(
    basin: Optional[str] = Query(None, description="Filter by basin"),
    operator: Optional[str] = Query(None, description="Filter by operator"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        query = (
            db.query(Well)
            .options(
                selectinload(Well.lasFiles),
                selectinload(Well.reports).selectinload(QualityReport.anomalies),
            )
        )

        is_admin = normalize_role(current_user.role) == "ADMIN"
        if not is_admin:
            query = query.filter(Well.ownerId == current_user.id)

        # Filters
        if basin and basin.strip() and basin.strip().upper() != "ALL":
            query = query.filter(func.lower(Well.basin) == basin.strip().lower())

        if operator and operator.strip() and operator.strip().upper() != "ALL":
            query = query.filter(func.lower(Well.operatorName) == operator.strip().lower())

        wells = query.order_by(desc(Well.updatedAt)).all()
        well_ids = [w.id for w in wells]

        # Available options for filter dropdowns (queried before filtering)
        all_wells_scope = db.query(Well)
        if not is_admin:
            all_wells_scope = all_wells_scope.filter(Well.ownerId == current_user.id)
        all_wells_for_filters = all_wells_scope.all()

        available_basins = sorted(list({w.basin for w in all_wells_for_filters if w.basin}))
        available_operators = sorted(list({w.operatorName for w in all_wells_for_filters if w.operatorName}))

        # Operator scores, Basin scores, Grade counts, and Well items
        operators_map: Dict[str, Dict[str, Any]] = {}
        basins_map: Dict[str, Dict[str, Any]] = {}
        grade_counts = {"EXCELLENT": 0, "GOOD": 0, "POOR": 0, "CRITICAL": 0}
        total_files = 0
        well_items = []

        for w in wells:
            op = w.operatorName or "Unknown Operator"
            b = w.basin or "Unknown Basin"
            file_count = len(w.lasFiles) if w.lasFiles else 0
            total_files += file_count

            # Anomaly count from reports
            well_anom_count = sum(r.anomalyCount for r in (w.reports or []))

            # Operators aggregation
            if op not in operators_map:
                operators_map[op] = {"totalScore": 0, "wells": 0, "files": 0}
            operators_map[op]["totalScore"] += w.qualityScore
            operators_map[op]["wells"] += 1
            operators_map[op]["files"] += file_count

            # Basins aggregation
            if b not in basins_map:
                basins_map[b] = {"totalScore": 0, "wells": 0, "files": 0}
            basins_map[b]["totalScore"] += w.qualityScore
            basins_map[b]["wells"] += 1
            basins_map[b]["files"] += file_count

            # Quality grade counting
            g = (w.qualityGrade or "").upper()
            if g in grade_counts:
                grade_counts[g] += 1
            elif w.qualityScore >= 90:
                grade_counts["EXCELLENT"] += 1
            elif w.qualityScore >= 75:
                grade_counts["GOOD"] += 1
            elif w.qualityScore >= 50:
                grade_counts["POOR"] += 1
            else:
                grade_counts["CRITICAL"] += 1

            well_items.append({
                "id": w.id,
                "name": w.name,
                "apiNo": w.apiNo,
                "operator": op,
                "field": w.fieldName or "Unknown Field",
                "basin": b,
                "qualityScore": w.qualityScore,
                "qualityGrade": w.qualityGrade or "UNKNOWN",
                "filesCount": file_count,
                "anomalyCount": well_anom_count,
                "tdFt": w.tdFt,
                "createdAt": w.createdAt.isoformat() if w.createdAt else None,
            })

        operator_scores = [
            {
                "operator": op,
                "score": round(data["totalScore"] / data["wells"]) if data["wells"] > 0 else 0,
                "files": data["files"],
                "wells": data["wells"],
            }
            for op, data in operators_map.items()
        ]
        operator_scores.sort(key=lambda x: x["score"], reverse=True)

        basin_scores = [
            {
                "basin": b,
                "score": round(data["totalScore"] / data["wells"]) if data["wells"] > 0 else 0,
                "wells": data["wells"],
                "files": data["files"],
            }
            for b, data in basins_map.items()
        ]
        basin_scores.sort(key=lambda x: x["score"], reverse=True)

        # Anomaly type distribution
        anomalies_counts = (
            db.query(
                Anomaly.anomalyType,
                func.count(Anomaly.id).label("count"),
            )
            .join(QualityReport, Anomaly.qualityReportId == QualityReport.id)
            .filter(QualityReport.wellId.in_(well_ids))
            .group_by(Anomaly.anomalyType)
            .order_by(desc("count"))
            .all()
            if well_ids
            else []
        )

        total_anomalies = sum(count for _, count in anomalies_counts)

        anomaly_distribution = [
            {
                "name": anom_type.replace("_", " "),
                "rawType": anom_type,
                "value": count,
                "percentage": round((count / total_anomalies) * 100, 1) if total_anomalies > 0 else 0,
                "color": ANOMALY_COLORS.get(anom_type, "#64748b"),
            }
            for anom_type, count in anomalies_counts
        ]

        # Severity distribution
        severity_counts = (
            db.query(
                Anomaly.severity,
                func.count(Anomaly.id).label("count"),
            )
            .join(QualityReport, Anomaly.qualityReportId == QualityReport.id)
            .filter(QualityReport.wellId.in_(well_ids))
            .group_by(Anomaly.severity)
            .order_by(desc("count"))
            .all()
            if well_ids
            else []
        )

        severity_distribution = [
            {
                "severity": (sev or "UNKNOWN").upper(),
                "count": count,
                "color": SEVERITY_COLORS.get((sev or "").upper(), "#94a3b8"),
            }
            for sev, count in severity_counts
        ]

        # Curve anomaly distribution (top 10 most impacted curve mnemonics)
        curve_anomalies_counts = (
            db.query(
                Anomaly.curveMnemonic,
                func.count(Anomaly.id).label("count"),
            )
            .join(QualityReport, Anomaly.qualityReportId == QualityReport.id)
            .filter(QualityReport.wellId.in_(well_ids))
            .group_by(Anomaly.curveMnemonic)
            .order_by(desc("count"))
            .limit(10)
            .all()
            if well_ids
            else []
        )

        curve_anomaly_distribution = [
            {
                "curve": (curve or "UNKNOWN").upper(),
                "count": count,
            }
            for curve, count in curve_anomalies_counts
        ]

        # Grade distribution
        grade_distribution = [
            {
                "grade": g,
                "count": count,
                "color": GRADE_COLORS.get(g, "#64748b"),
            }
            for g, count in grade_counts.items()
        ]

        # Summary KPIs
        avg_score = round(sum(w.qualityScore for w in wells) / len(wells)) if wells else 0
        critical_count = sum(count for sev, count in severity_counts if (sev or "").upper() in ("CRITICAL", "HIGH"))
        clean_count = sum(1 for w in wells if w.qualityScore >= 75)
        flagged_count = len(wells) - clean_count

        top_operator = operator_scores[0]["operator"] if operator_scores else "N/A"
        top_basin = basin_scores[0]["basin"] if basin_scores else "N/A"

        summary = {
            "totalWells": len(wells),
            "totalFiles": total_files,
            "avgQualityScore": avg_score,
            "totalAnomalies": total_anomalies,
            "criticalAnomalies": critical_count,
            "cleanWellsCount": clean_count,
            "flaggedWellsCount": flagged_count,
            "topOperator": top_operator,
            "topBasin": top_basin,
        }

        return {
            "summary": summary,
            "operatorScores": operator_scores,
            "basinScores": basin_scores,
            "anomalyDistribution": anomaly_distribution,
            "severityDistribution": severity_distribution,
            "curveAnomalyDistribution": curve_anomaly_distribution,
            "gradeDistribution": grade_distribution,
            "wells": well_items,
            "availableBasins": available_basins,
            "availableOperators": available_operators,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load analytics: {e}",
        )

