# WellQC — Interactive Visual Kanban Board & Trello Free Import Guide

> **Project:** WellQC — AI-Powered Well Log Quality Assurance & Subsurface Analytics Platform  
> **Agile Framework:** 7 Sprints · 14 Weeks · 8 Team Members  
> **Overall Platform Completion:** **98%** (Sprints 1–6 Completed, Sprint 7 in Final Verification)  

---

## 💡 How to Beat the 20-Card Limit on Trello Free Plan

Trello's CSV Importer Power-Up imposes a **20-row limit on free accounts**. Furthermore, team member initials (`SE1`, `DA1`, etc.) will show as unassigned unless you purchase 8 paid Trello seats.

We have solved both issues for you in two zero-cost ways:

1. **Pre-Split CSV Batches (≤ 20 cards each):** Simply import 3 small CSV files in under 2 minutes. No upgrade needed!
2. **Embedded Card Titles:** Member roles and domains (`[SE1][Backend]`) are now directly embedded in the card titles so they appear boldly on the card faces without needing member accounts or label setup.
3. **Native Multi-Card Paste (0 Power-Ups):** Copy any code block below, paste it directly into Trello's *+ Add a card*, and click *Create X cards* to generate the whole list in 2 seconds.

---

## 📥 1. Free-Tier Import Files (All ≤ 20 Rows)

Upload these 3 files consecutively into your Trello board via the CSV Importer Power-Up:

| Batch File | Contents | Card Count | Status | Direct File Link |
|---|---|---|---|---|
| **`batch_1_sprints_1_to_3.csv`** | Sprints 1, 2, and 3 | **19 cards** (≤ 20 limit) | Free Eligible | [**`batch_1_sprints_1_to_3.csv`**](file:///c:/Users/Ekwebelam%20C%20Williams/Desktop/NDI-G5/wellqc/Documentations/trello_batches/batch_1_sprints_1_to_3.csv) |
| **`batch_2_sprints_4_to_5.csv`** | Sprints 4 and 5 | **12 cards** (≤ 20 limit) | Free Eligible | [**`batch_2_sprints_4_to_5.csv`**](file:///c:/Users/Ekwebelam%20C%20Williams/Desktop/NDI-G5/wellqc/Documentations/trello_batches/batch_2_sprints_4_to_5.csv) |
| **`batch_3_sprints_6_to_7.csv`** | Sprints 6 and 7 | **19 cards** (≤ 20 limit) | Free Eligible | [**`batch_3_sprints_6_to_7.csv`**](file:///c:/Users/Ekwebelam%20C%20Williams/Desktop/NDI-G5/wellqc/Documentations/trello_batches/batch_3_sprints_6_to_7.csv) |

> Alternatively, if you prefer importing sprint by sprint, individual CSV files are available in [**`Documentations/trello_batches/`**](file:///c:/Users/Ekwebelam%20C%20Williams/Desktop/NDI-G5/wellqc/Documentations/trello_batches/).

---

## ⚡ 2. Instant 1-Click Copy-Paste Blocks (No Power-Ups Needed)

In Trello, create a list, click **+ Add a card**, paste the block, press **Enter**, and select **"Create X cards"**:

### 📋 List: `Sprint 1: Discovery, Architecture & Core Stack`
```text
[DA1] [Petrophysics] Petrophysical Domain Modeling & Curve Physical Limits (✅)
[SE1] [Backend] LAS 2.0 Parser Engine & Line Splitter Validation (✅)
[SE2] [Frontend] Next.js 15 App Shell, Navigation & Design System (✅)
[CE2] [DevOps & Cloud] Database Schema Design & Prisma Setup (✅)
[CE1] [DevOps & Cloud] CI/CD Pipeline Setup & Repository Governance (✅)
[SE1] [Milestone] Milestone: Core Architecture & Ingestion Proof-of-Concept (✅)
```

### 📋 List: `Sprint 2: Foundation, Auth & Multi-Tenant Database`
```text
[CE2] [DevOps & Cloud] Multi-Tenant PostgreSQL Architecture on Neon (✅)
[SE2] [Security] Authentication Engine, Session Tokens & Scrypt Hashing (✅)
[DA1] [Petrophysics] Mnemonic Dictionary & 14 Standard Curve Classifications (✅)
[DA2] [Petrophysics] Wireline Curve Anomaly Classification & Root Cause Engine (✅)
[SE2] [Frontend] File Upload UI with Drag-and-Drop & Pre-Validation (✅)
[CE1] [DevOps & Cloud] Vercel Preview Deployments & DB Migration Automation (✅)
[SE2] [Milestone] Milestone: Authenticated Ingestion & Mnemonic Baseline (✅)
```

### 📋 List: `Sprint 3: Core Engine, Quality Scoring & Ingestion Workspace`
```text
[SE1] [Backend] Multi-Factor Quality Scoring Algorithm (Completeness/Integrity/Noise) (✅)
[SE2] [Frontend] Upload Workspace Redesign & Modular Tabbed Layout (✅)
[DA3] [Frontend] Subsurface Basin Analytics & KPI Dashboard Aggregations (✅)
[DA4] [Compliance] Automated PDF Audit Report Generator (✅)
[CE2] [Completed] Atomic Transaction Ingestion Pipeline & Downsampling (✅)
[SE1] [Milestone] Milestone: Complete Quality Scoring & PDF Audit Capability (✅)
```

### 📋 List: `Sprint 4: Advanced Visualisation, Imputation & Python Migration`
```text
[SE1] [Backend] FastAPI Microservice Migration & Native NumPy/Pandas Stack (✅)
[SE2] [Frontend] SVG Multi-Track Wireline Log Viewer with Depth Sync (✅)
[DA1] [Petrophysics] Custom Mnemonic Aliases & Tenant Rule Management (✅)
[DA2] [Backend] Imputation Algorithm Benchmark (KNN, Spline, Iterative SVD) (✅)
[CE1] [Completed] Zero-Mock Clean Seeder & Performance Load Testing (✅)
[SE1] [Milestone] Milestone: Unified Python Backend & Interactive Log Viewer (✅)
```

### 📋 List: `Sprint 5: Security Hardening, Default-to-Deny RBAC & Admin Tools`
```text
[SE1] [Security] Server-Side RBAC Enforcement & Ghost Token Elimination (✅)
[SE1] [Security] Self-Registration Role Escalation Block (403 on ADMIN role) (✅)
[CE2] [Security] Interactive Admin Management CLI (`manage_admin.py`) (✅)
[SE2] [Security] Admin Panel UI with Tabbed User Management & Tokens (✅)
[DA4] [Security] Automated Security Test Suite (14 Tests in `test_admin_auth.py`) (✅)
[SE1] [Milestone] Milestone: Default-to-Deny Security & Administrative Center (✅)
```

### 📋 List: `Sprint 6: Production Hardening & Quality Engine 12-Item Overhaul`
```text
[SE1] [Petrophysics] Item 1-2: Per-Row Anomaly Approvals & Specific Method Routing (✅)
[DA2] [Backend] Item 3: AUTO Imputation Gap Ranking via Cross-Validation (✅)
[DA1] [Frontend] Item 4: Impossible Values Action Suite (Remove / Clip / Delete Row) (✅)
[DA2] [Completed] Item 5: Long Null Cluster Guards & Unfillable Flag Boundaries (✅)
[SE1] [Completed] Item 6-7: Duplicate Depth Prune & 2-Point Neighbour Despiking (✅)
[DA4] [Compliance] Item 8-9: Real Change Report Telemetry & Audit Certificate ID (✅)
[SE2] [Frontend] Item 10-12: Staged Non-Destructive QA UI & Cleaned Export Suite (✅)
[CE2] [Security] Sliding-Window IP Rate Limiter & Security Stabilization (✅)
[SE1] [Milestone] Milestone: Certified Quality Engine Overhaul & Audit Pipeline (✅)
```

### 📋 List: `Sprint 7: Multi-Well Comparison, NUPRC Compliance & Batch Processing`
```text
[SE1] [Backend] Multi-Well Depth Alignment & Correlation Engine (SE1) (✅)
[SE2] [Frontend] Cross-Well Canvas UI with Synchronized Depth Scrolling (SE2) (🔄 95%)
[SE1] [Petrophysics] Unsupervised ML Lithology Classification on GR-RHOB-NPHI (SE1) (🔄 85%)
[SE2] [Compliance] NUPRC Compliance Report Template & Digital Signatures (SE2, DA4) (🔄 90%)
[DA1] [Petrophysics] Niger Delta Formation Cutoffs (Akata, Agbada, Benin) (DA1, DA2) (✅)
[DA3] [Petrophysics] Offset Niger Delta Demonstration Well Package Curation (DA3) (🔄 95%)
[CE1] [In Progress] Asynchronous Batch Ingestion Background Workers & Live Progress (CE1) (🔄 85%)
[CE2] [Backend] Outbound Webhook Event Dispatcher for Cloud Storage Sync (CE2) (🔄 80%)
[SE1] [Frontend] End-to-End System Integration & Acceptance Testing Suite (All) (🔄 95%)
[SE1] [Milestone] Milestone: Final Production Platform Release & NUPRC Audit Readiness (🔄 75%)
```

---

## 📊 3. Master Visual Kanban Schedule Table

### 🗂️ Sprint 1: Discovery, Architecture & Core Stack — Status: `100%`
**Timeline:** 2026-07-20 to 2026-07-31  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#3** | [DA1] [Petrophysics] Petrophysical Domain Modeling & Curve Physical Limits (✅) | `DA1, DA2` | ✅ **100%** | `Petrophysics` `Completed` | 2026-07-24 |
| **#4** | [SE1] [Backend] LAS 2.0 Parser Engine & Line Splitter Validation (✅) | `SE1` | ✅ **100%** | `Backend` `Completed` | 2026-07-29 |
| **#5** | [SE2] [Frontend] Next.js 15 App Shell, Navigation & Design System (✅) | `SE2` | ✅ **100%** | `Frontend` `Completed` | 2026-07-28 |
| **#6** | [CE2] [DevOps & Cloud] Database Schema Design & Prisma Setup (✅) | `CE2` | ✅ **100%** | `DevOps & Cloud` `Completed` | 2026-07-30 |
| **#7** | [CE1] [DevOps & Cloud] CI/CD Pipeline Setup & Repository Governance (✅) | `CE1` | ✅ **100%** | `DevOps & Cloud` `Completed` | 2026-07-25 |
| **#8** | [SE1] [Milestone] Milestone: Core Architecture & Ingestion Proof-of-Concept (✅) | `SE1, SE2, CE1, CE2` | ✅ **100%** | `Milestone` `Completed` | 2026-07-31 |

---

### 🗂️ Sprint 2: Foundation, Auth & Multi-Tenant Database — Status: `100%`
**Timeline:** 2026-08-03 to 2026-08-14  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#10** | [CE2] [DevOps & Cloud] Multi-Tenant PostgreSQL Architecture on Neon (✅) | `CE2` | ✅ **100%** | `DevOps & Cloud` `Completed` | 2026-08-07 |
| **#11** | [SE2] [Security] Authentication Engine, Session Tokens & Scrypt Hashing (✅) | `SE2, CE2` | ✅ **100%** | `Security` `Completed` | 2026-08-11 |
| **#12** | [DA1] [Petrophysics] Mnemonic Dictionary & 14 Standard Curve Classifications (✅) | `DA1` | ✅ **100%** | `Petrophysics` `Completed` | 2026-08-07 |
| **#13** | [DA2] [Petrophysics] Wireline Curve Anomaly Classification & Root Cause Engine (✅) | `DA2` | ✅ **100%** | `Petrophysics` `Completed` | 2026-08-12 |
| **#14** | [SE2] [Frontend] File Upload UI with Drag-and-Drop & Pre-Validation (✅) | `SE2` | ✅ **100%** | `Frontend` `Completed` | 2026-08-13 |
| **#15** | [CE1] [DevOps & Cloud] Vercel Preview Deployments & DB Migration Automation (✅) | `CE1` | ✅ **100%** | `DevOps & Cloud` `Completed` | 2026-08-14 |
| **#16** | [SE2] [Milestone] Milestone: Authenticated Ingestion & Mnemonic Baseline (✅) | `SE2, CE2, DA1` | ✅ **100%** | `Milestone` `Petrophysics` `Completed` | 2026-08-14 |

---

### 🗂️ Sprint 3: Core Engine, Quality Scoring & Ingestion Workspace — Status: `100%`
**Timeline:** 2026-08-17 to 2026-08-28  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#18** | [SE1] [Backend] Multi-Factor Quality Scoring Algorithm (Completeness/Integrity/Noise) (✅) | `SE1, DA1` | ✅ **100%** | `Backend` `Completed` | 2026-08-21 |
| **#19** | [SE2] [Frontend] Upload Workspace Redesign & Modular Tabbed Layout (✅) | `SE2` | ✅ **100%** | `Frontend` `Completed` | 2026-08-24 |
| **#20** | [DA3] [Frontend] Subsurface Basin Analytics & KPI Dashboard Aggregations (✅) | `DA3` | ✅ **100%** | `Frontend` `Completed` | 2026-08-25 |
| **#21** | [DA4] [Compliance] Automated PDF Audit Report Generator (✅) | `DA4` | ✅ **100%** | `Compliance` `Completed` | 2026-08-27 |
| **#22** | [CE2] [Completed] Atomic Transaction Ingestion Pipeline & Downsampling (✅) | `CE2` | ✅ **100%** | `Completed` | 2026-08-26 |
| **#23** | [SE1] [Milestone] Milestone: Complete Quality Scoring & PDF Audit Capability (✅) | `SE1, SE2, DA1, DA4` | ✅ **100%** | `Milestone` `Backend` `Compliance` `Completed` | 2026-08-28 |

---

### 🗂️ Sprint 4: Advanced Visualisation, Imputation & Python Migration — Status: `100%`
**Timeline:** 2026-08-31 to 2026-09-11  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#25** | [SE1] [Backend] FastAPI Microservice Migration & Native NumPy/Pandas Stack (✅) | `SE1, CE2` | ✅ **100%** | `Backend` `Completed` | 2026-09-07 |
| **#26** | [SE2] [Frontend] SVG Multi-Track Wireline Log Viewer with Depth Sync (✅) | `SE2` | ✅ **100%** | `Frontend` `Completed` | 2026-09-08 |
| **#27** | [DA1] [Petrophysics] Custom Mnemonic Aliases & Tenant Rule Management (✅) | `DA1` | ✅ **100%** | `Petrophysics` `Completed` | 2026-09-08 |
| **#28** | [DA2] [Backend] Imputation Algorithm Benchmark (KNN, Spline, Iterative SVD) (✅) | `DA2` | ✅ **100%** | `Backend` `ML & Analytics` `Completed` | 2026-09-09 |
| **#29** | [CE1] [Completed] Zero-Mock Clean Seeder & Performance Load Testing (✅) | `CE1, DA3` | ✅ **100%** | `Completed` | 2026-09-10 |
| **#30** | [SE1] [Milestone] Milestone: Unified Python Backend & Interactive Log Viewer (✅) | `SE1, SE2, CE2` | ✅ **100%** | `Milestone` `Backend` `Frontend` `Completed` | 2026-09-11 |

---

### 🗂️ Sprint 5: Security Hardening, Default-to-Deny RBAC & Admin Tools — Status: `100%`
**Timeline:** 2026-09-14 to 2026-09-25  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#32** | [SE1] [Security] Server-Side RBAC Enforcement & Ghost Token Elimination (✅) | `SE1, CE2` | ✅ **100%** | `Security` `Completed` | 2026-09-18 |
| **#33** | [SE1] [Security] Self-Registration Role Escalation Block (403 on ADMIN role) (✅) | `SE1` | ✅ **100%** | `Security` `Completed` | 2026-09-21 |
| **#34** | [CE2] [Security] Interactive Admin Management CLI (`manage_admin.py`) (✅) | `CE2` | ✅ **100%** | `Security` `Completed` | 2026-09-22 |
| **#35** | [SE2] [Security] Admin Panel UI with Tabbed User Management & Tokens (✅) | `SE2` | ✅ **100%** | `Security` `Frontend` `Completed` | 2026-09-24 |
| **#36** | [DA4] [Security] Automated Security Test Suite (14 Tests in `test_admin_auth.py`) (✅) | `DA4, CE1` | ✅ **100%** | `Security` `Frontend` `Completed` | 2026-09-25 |
| **#37** | [SE1] [Milestone] Milestone: Default-to-Deny Security & Administrative Center (✅) | `SE1, SE2, CE2` | ✅ **100%** | `Milestone` `Security` `Completed` | 2026-09-25 |

---

### 🗂️ Sprint 6: Production Hardening & Quality Engine 12-Item Overhaul — Status: `100%`
**Timeline:** 2026-09-28 to 2026-10-09  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#39** | [SE1] [Petrophysics] Item 1-2: Per-Row Anomaly Approvals & Specific Method Routing (✅) | `SE1, SE2` | ✅ **100%** | `Petrophysics` `Completed` | 2026-10-02 |
| **#40** | [DA2] [Backend] Item 3: AUTO Imputation Gap Ranking via Cross-Validation (✅) | `DA2, SE1` | ✅ **100%** | `Backend` `Completed` | 2026-10-05 |
| **#41** | [DA1] [Frontend] Item 4: Impossible Values Action Suite (Remove / Clip / Delete Row) (✅) | `DA1, SE1` | ✅ **100%** | `Frontend` `Completed` | 2026-10-06 |
| **#42** | [DA2] [Completed] Item 5: Long Null Cluster Guards & Unfillable Flag Boundaries (✅) | `DA2, DA1` | ✅ **100%** | `Completed` | 2026-10-06 |
| **#43** | [SE1] [Completed] Item 6-7: Duplicate Depth Prune & 2-Point Neighbour Despiking (✅) | `SE1` | ✅ **100%** | `Completed` | 2026-10-07 |
| **#44** | [DA4] [Compliance] Item 8-9: Real Change Report Telemetry & Audit Certificate ID (✅) | `DA4, SE1` | ✅ **100%** | `Compliance` `Completed` | 2026-10-08 |
| **#45** | [SE2] [Frontend] Item 10-12: Staged Non-Destructive QA UI & Cleaned Export Suite (✅) | `SE2` | ✅ **100%** | `Frontend` `Completed` | 2026-10-09 |
| **#46** | [CE2] [Security] Sliding-Window IP Rate Limiter & Security Stabilization (✅) | `CE2, CE1` | ✅ **100%** | `Security` `Completed` | 2026-10-02 |
| **#47** | [SE1] [Milestone] Milestone: Certified Quality Engine Overhaul & Audit Pipeline (✅) | `SE1, SE2, DA1, DA2, DA4` | ✅ **100%** | `Milestone` `Compliance` `Completed` | 2026-10-09 |

---

### 🗂️ Sprint 7: Multi-Well Comparison, NUPRC Compliance & Batch Processing — Status: `88%`
**Timeline:** 2026-10-12 to 2026-10-23  

| ID | Card Title & Assignment | Assignees | Progress | Labels | Due Date |
|---|---|---|---|---|---|
| **#49** | [SE1] [Backend] Multi-Well Depth Alignment & Correlation Engine (SE1) (✅) | `SE1` | ✅ **100%** | `Backend` `Completed` | 2026-10-16 |
| **#50** | [SE2] [Frontend] Cross-Well Canvas UI with Synchronized Depth Scrolling (SE2) (🔄 95%) | `SE2` | 🔄 **95%** | `Frontend` `In Progress` | 2026-10-19 |
| **#51** | [SE1] [Petrophysics] Unsupervised ML Lithology Classification on GR-RHOB-NPHI (SE1) (🔄 85%) | `SE1, DA2` | 🔄 **85%** | `Petrophysics` `ML & Analytics` `In Progress` | 2026-10-20 |
| **#52** | [SE2] [Compliance] NUPRC Compliance Report Template & Digital Signatures (SE2, DA4) (🔄 90%) | `SE2, DA4` | 🔄 **90%** | `Compliance` `In Progress` | 2026-10-20 |
| **#53** | [DA1] [Petrophysics] Niger Delta Formation Cutoffs (Akata, Agbada, Benin) (DA1, DA2) (✅) | `DA1, DA2` | ✅ **100%** | `Petrophysics` `Completed` | 2026-10-16 |
| **#54** | [DA3] [Petrophysics] Offset Niger Delta Demonstration Well Package Curation (DA3) (🔄 95%) | `DA3` | 🔄 **95%** | `Petrophysics` `In Progress` | 2026-10-19 |
| **#55** | [CE1] [In Progress] Asynchronous Batch Ingestion Background Workers & Live Progress (CE1) (🔄 85%) | `CE1` | 🔄 **85%** | `In Progress` | 2026-10-21 |
| **#56** | [CE2] [Backend] Outbound Webhook Event Dispatcher for Cloud Storage Sync (CE2) (🔄 80%) | `CE2` | 🔄 **80%** | `Backend` `DevOps & Cloud` `In Progress` | 2026-10-22 |
| **#57** | [SE1] [Frontend] End-to-End System Integration & Acceptance Testing Suite (All) (🔄 95%) | `SE1, SE2, CE1, CE2, DA1, DA2, DA3, DA4` | 🔄 **95%** | `Frontend` `In Progress` | 2026-10-23 |
| **#58** | [SE1] [Milestone] Milestone: Final Production Platform Release & NUPRC Audit Readiness (🔄 75%) | `SE1, SE2, CE1, CE2, DA1, DA2, DA3, DA4` | 🔄 **75%** | `Milestone` `Compliance` `In Progress` | 2026-10-23 |

---
