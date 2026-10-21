# BAMOE v8 → v9.5 Migration Inventory

**Project:** `<name>` (`<groupId>:<artifactId>:<version>`)
**Source directory (v8):** `v8-projects/<project-name>/`
**Output directory (v9):** `v9-projects/<v9-name>/`
**Audit date:** `<YYYY-MM-DD>`
**Audited by:** BAMOE Migrator

> This file is a template. It is overwritten by Sub-Task 1 (audit) each time a
> migration runs. Per-project inventories also live at
> `v9-projects/<v9-name>/migration-inventory.md`.

---

## 1. Project Identity

| Property | Value |
|---|---|
| Maven coordinates | |
| Packaging | |
| Display name | |
| Description | |
| v8 KIE version | |
| Build Java runtime | |
| Build Maven version | |

---

## 2. Asset Inventory

### 2.1 BPMN Workflow Files

| File | Process ID | Process Name | Issues |
|---|---|---|---|

### 2.2 DMN Decision Files

| File | Model Name | Issues |
|---|---|---|

### 2.3 DRL / Rules / Test Scenarios

| File | Type | Issues |
|---|---|---|

### 2.4 Forms (`.frm`)

| File | Bound to | Issues |
|---|---|---|

### 2.5 Custom Java (WIH, callbacks, listeners)

| File | Role | Issues |
|---|---|---|

### 2.6 Configuration Files (to be deleted in v9)

| File | Replaced by |
|---|---|
| `kmodule.xml` | `application.properties` |
| `kie-deployment-descriptor.xml` | `application.properties` |
| `persistence.xml` | `application.properties` |
| `project.repositories` / `project.imports` | `pom.xml` |

---

## 3. Classification Summary

| Classification | Count | Assets |
|---|---|---|
| Migrate as-is | 0 | |
| Requires manual update | 0 | |
| Must replace | 0 | |

---

## 4. Flags and Blockers

<!-- PMML, guided rules, DSL, scorecards, shared KIE sessions, hyphenated
     process IDs, JavaScript script tasks, DROOLS gateway expressions -->
