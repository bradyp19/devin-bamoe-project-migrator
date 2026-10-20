# Migration Inventory

**Source Path:** `v8-projects/v8-app/`
**Target Path:** `v9-projects/v9-app/`

**Project:** Evaluation_Process (Employee evaluation workflow)
**v8 Version:** 7.67.2.Final-redhat-00017
**v9 Target:** 9.5.x

---

## Asset Summary

| Asset Type | Count | Migration Action | Notes |
|------------|-------|-------------------|-------|
| BPMN | 1 | Migrate as-is | Process ID "evaluation" (no hyphens/dots - OK) |
| DRL | 0 | N/A | None present |
| DMN | 0 | N/A | None present |
| Decision Tables (XLS/XLSX) | 0 | N/A | None present |
| PMML | 0 | N/A | None present |
| Guided Rules | 0 | N/A | None present |
| Guided Decision Tables | 0 | N/A | None present |
| DSL/DSLR | 0 | N/A | None present |
| Scorecards | 0 | N/A | None present |
| Forms (.frm) | 2 | **Must replace** | evaluation-taskform.frm, PerformanceEvaluation-taskform.frm |
| Test Scenarios (.scesim) | 0 | N/A | None present |
| WID Files | 0 | N/A | None present |
| WIH Java Classes | 0 | N/A | None present |
| Custom UserGroupCallback | 0 | N/A | None present |
| Custom AssignmentStrategy | 0 | N/A | None present |
| Custom Event Listeners | 0 | N/A | None present |
| Case Management (CMMN) | 0 | N/A | None present |
| Java Domain Classes | 0 | N/A | None present (src/main/java is empty) |

---

## BPMN Analysis

**File:** `src/main/resources/evaluation.bpmn`

**Process ID:** `evaluation`
- Status: ✅ **Compatible** (no hyphens or dots)

**Process Variables:**
- `employee` (String)
- `reason` (String)
- `performance` (Integer)
- `initiator` (String)

**Tasks:**
- 3 User Tasks:
  1. Self Evaluation (ID: `_D3E17247-1D94-47D8-93AD-D645E317B736`)
  2. PM Evaluation (ID: `_E35438DF-03AF-4D7B-9DCB-30BC70E7E92E`)
  3. HR Evaluation (ID: `_AB431E82-86BC-460F-9D8B-7A7617565B36`)

**Gateways:**
- 2 Parallel Gateways (diverging and converging)
- Status: ✅ **Compatible** (no conditional expressions requiring conversion)

**Script Tasks:**
- None present
- Status: ✅ **Compatible** (no JavaScript to convert)

**Shared KIE Session Patterns:**
- No `insert()`, `retract()`, `update()`, or `delete()` calls found
- Status: ✅ **Compatible** (no refactor needed)

**Expression Language:**
- `expressionLanguage="http://www.mvel.org/2.0"` in BPMN header
- Note: v9 uses Java expressions by default; this will be handled during BPMN open/save in Developer Tools

---

## Configuration Files (To Delete)

The following v8 configuration files must be **deleted** in v9 (replaced by `application.properties`):

| File | Reason |
|------|--------|
| `src/main/resources/META-INF/kmodule.xml` | Not needed in v9 (KIE bases declared in code) |
| `src/main/resources/META-INF/kie-deployment-descriptor.xml` | Not needed in v9 (config moved to Java beans + application.properties) |
| `src/main/resources/META-INF/persistence.xml` | Not needed in v9 (persistence configured in application.properties) |
| `project.imports` | Not needed in v9 (imports handled in source code) |
| `project.repositories` | Not needed in v9 (use standard Maven settings.xml) |

---

## POM Analysis

**File:** `pom.xml`

**Current State:**
- `packaging`: `kjar` → **Must change to** `jar`
- `groupId`: `evaluation`
- `artifactId`: `evaluation`
- `version`: `1.0.0-SNAPSHOT`

**Dependencies to Replace:**
- `org.kie:kie-api:7.67.2.Final-redhat-00017` → Remove (managed by Kogito BOM)
- `org.kie:kie-internal:7.67.2.Final-redhat-00017` → Remove (managed by Kogito BOM)
- `junit:junit:4.12` → **Must upgrade to** JUnit 5 (junit-jupiter)
- `com.thoughtworks.xstream:xstream:1.4.11` → Review necessity (likely test-only, may not be needed)

**BOM to Add:**
- `com.ibm.bamoe:bamoe-quarkus-bom:9.5.x` (imports Kogito + Quarkus transitively)

**Plugin to Replace:**
- `org.kie:kie-maven-plugin:7.67.2.Final-redhat-00017` → Remove (not needed in v9)

---

## Forms Analysis

**Files Found:**
1. `src/main/resources/evaluation-taskform.frm`
2. `src/main/resources/PerformanceEvaluation-taskform.frm`

**Action Required:**
- ✅ **Both forms must be regenerated** using BAMOE Developer Tools
- Command: "Generate form code for User Task" for each User Task in the BPMN
- Legacy `.frm` files are **incompatible** with v9 (cannot be migrated directly)

---

## Environment Check

**Prerequisites Status:**

| Requirement | Status | Notes |
|-------------|--------|-------|
| Java 21 | ❌ Not installed | Java runtime not found on system |
| Maven 3.9.11+ | ❌ Not installed | Maven command not found |
| Git | ✅ Available | System has git |
| VS Code | ℹ️ Not checked | User to verify |
| BAMOE Developer Tools | ℹ️ Not checked | User to verify in VS Code Extensions |
| BAMOE Maven Repository | ℹ️ Not checked | User to configure in ~/.m2/settings.xml |

**Action Required:**
- Install Java 21 (IBM Semeru or Eclipse Temurin)
- Install Maven 3.9.11+
- Configure BAMOE Maven Repository in `~/.m2/settings.xml`
- Install BAMOE Developer Tools extension in VS Code

---

## Migration Complexity Assessment

**Overall Complexity:** ⭐ Low

**Reasoning:**
- Simple BPMN workflow with 3 User Tasks and 2 Parallel Gateways
- No complex constructs requiring conversion (no JavaScript, no DROOLS expressions, no shared KIE session patterns)
- No DRL, DMN, decision tables, or rules to migrate
- No custom WIHs, event listeners, or security classes
- Main work: POM restructuring, config file deletion, and form regeneration

**Estimated Effort:**
- Sub-Task 1 (Audit): ✅ Complete
- Sub-Task 2 (POM/Structure): ~30 minutes
- Sub-Task 3 (BPMN): ~15 minutes (open/save in Developer Tools)
- Sub-Task 4 (DMN): N/A (no DMN)
- Sub-Task 5 (DRL/Test Scenarios): N/A (no DRL)
- Sub-Task 6 (WIH): N/A (no WIH)
- Sub-Task 7 (Security): ~15 minutes (OIDC configuration, though non-secured mode may suffice for dev)
- Sub-Task 8 (Forms): ~30 minutes (regenerate 2 forms)
- Sub-Task 9 (Event Streaming): N/A (no event listeners)
- Sub-Task 10 (Deployment): ~45 minutes (build, deploy, smoke test)

**Total Estimated Time:** ~2-3 hours (excluding prerequisite setup)

---

## Blocking Issues

None identified. The project is straightforward with no unsupported features.

---

## Next Steps

1. **Install Prerequisites:**
   - Install Java 21
   - Install Maven 3.9.11+
   - Configure BAMOE Maven Repository in `~/.m2/settings.xml`
   - Install BAMOE Developer Tools for VS Code

2. **Proceed to Sub-Task 2:**
   - Create `v9-projects/v9-app/` directory
   - Generate new `pom.xml` using BAMOE Canvas Quarkus Accelerator template
   - Delete v8 configuration files
   - Create `application.properties` skeleton
   - Run `mvn clean package -DskipTests` to verify build

---

**Inventory Generated:** 2026-10-07
**Status:** ✅ Sub-Task 1 Complete
