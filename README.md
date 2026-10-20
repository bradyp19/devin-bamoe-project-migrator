# BAMOE v8 → v9.5 Project Migrator

Turns your old IBM BAMOE v8 project into a new BAMOE v9.5 project, automatically, using Devin.

---

## Three steps

```
1. Put your v8 project folder (or .zip) into  v8-projects/
2. Open Devin on the web → choose this repository → New session
3. Type:   Migrate my project
```

That's it. Devin will do the rest and tell you when it's done.

> **How do I "put a folder in"?** On GitHub, open the `v8-projects/` folder, click **Add file → Upload files**, drag your folder or .zip in, and click **Commit changes**. No command line needed.

---

## What goes in

A correct input looks exactly like this:

```
v8-projects/
└── my-project/                               ← any name; a .zip is fine too
    ├── pom.xml                               ← MUST be right here, not one folder deeper
    └── src/
        └── main/
            ├── java/                         ← your Java classes (may be empty)
            └── resources/
                ├── *.bpmn                    ← your process diagrams
                ├── *.dmn  *.drl  *.frm       ← decisions, rules, forms (optional)
                └── META-INF/
                    ├── kmodule.xml           ← normal in v8; will be removed in v9
                    ├── kie-deployment-descriptor.xml
                    └── persistence.xml
```

If your folder looks like this, you're good. If you're not sure, just put it in and ask Devin: *"Is my project in the right place?"*

---

## What comes out

```
v9-projects/
└── my-project/
    ├── pom.xml                               ← new; Quarkus + Kogito
    ├── migration-inventory.md                ← everything Devin found in your v8 project
    ├── migration-status.md                   ← the 10 steps, ticked off as they finish
    └── src/main/
        ├── java/…                            ← updated Java (jakarta.*, new handlers)
        └── resources/
            ├── application.properties        ← replaces all the META-INF xml files
            ├── *.bpmn                        ← upgraded diagrams, Java scripts
            └── custom-forms-dev/*.tsx        ← regenerated forms (if you had .frm files)
```

---

## What you will see

Devin works through 10 steps. Here's what each one looks like in plain language:

| Step | What Devin says it's doing | What appears | Typical time |
|---|---|---|---|
| 1 | "Auditing your v8 project" | `migration-inventory.md` — a list of everything found | 1–2 min |
| 2 | "Creating the new v9 project structure" | `v9-projects/<name>/pom.xml` + `application.properties` | 1–2 min |
| 3 | "Reading your process diagrams and rewriting any JavaScript inside them as Java" | upgraded `.bpmn` files | 2–5 min |
| 4 | "Checking decision models (DMN)" | upgraded `.dmn` files, or "skipped — none found" | 0–3 min |
| 5 | "Checking rules and test scenarios" | converted `.drl`/`.scesim` files, or "skipped" | 0–3 min |
| 6 | "Updating your custom Java work handlers" | rewritten Java classes, or "skipped" | 0–5 min |
| 7 | "Moving security settings to the new login system" | security lines in `application.properties` | 1–3 min |
| 8 | "Regenerating your forms" | new `.tsx` form files under `custom-forms-dev/` | 2–5 min |
| 9 | "Checking event listeners and messaging" | listener classes / Kafka properties, or "skipped" | 0–3 min |
| 10 | "Writing down how to go live" | deployment notes for the new version | 1–2 min |

At the end Devin posts a summary like:

```
Done! I migrated your project "my-project" from BAMOE v8 to v9.5.

Found:      2 processes, 3 forms, 1 rule file, 0 decision models.
Created:    v9-projects/my-project/  (see migration-status.md for what was done)
To do by hand:
  - Open the regenerated forms in BAMOE Developer Tools for VS Code and check the layout.
  - Your v8 database cannot be reused — the deployment notes explain the side-by-side switchover.
```

On the Devin website Devin cannot run the IBM build tool, so `Build: not-run` is normal. The converted files are still complete. If you want a verified build, see [docs/engineers/local-maven-repo.md](docs/engineers/local-maven-repo.md).

---

## Common pitfalls

| What you see | Why | Fix |
|---|---|---|
| I uploaded a .zip | That's fine — Devin unzips it automatically | Nothing. If Devin says it can't find `pom.xml`, the zip probably contains a folder inside a folder; Devin fixes that too. Otherwise unzip it yourself and put the inner folder in `v8-projects/` |
| "I can't find pom.xml" | The folder is in the wrong place (repo root, `v9-projects/`, or nested twice) | Move it so `v8-projects/<name>/pom.xml` exists |
| Folder name has spaces ("my app copy") | Spaces break some tools | Devin renames it with hyphens; prefer no spaces next time |
| Only a .bpmn file, no pom.xml | A single diagram is not a project export | In Business Central use **Export** (or git clone the project) so you get `pom.xml` + `src/` |
| Two folders in `v8-projects/` | Devin doesn't know which to migrate | It will ask. Say "all" or a name |
| "Build: not-run" | Expected on the Devin website — the IBM build repo is private | Nothing; the files are complete. See the engineers' appendix for a local verified build |
| Forms look missing | `.frm` forms can't be converted automatically | Devin generates new ones you may need to open and tweak in BAMOE Developer Tools for VS Code |
| Devin asks a question and waits | It only asks when it truly can't decide | Just answer in plain words |

---

## Video tutorial

Watch the existing demo: [BAMOE Migrator on YouTube](https://www.youtube.com/watch?v=e5pNUnvGr9Y).

A new end-to-end tutorial is in the works — see [docs/tutorial/video-script.md](docs/tutorial/video-script.md) for what it will cover.

---
---

## Details for engineers

Everything below is the technical reference. Non-engineers can stop here.

### The migration plan at a glance

The full plan lives in [`bamoe-v8-to-v9-migration-plan.md`](bamoe-v8-to-v9-migration-plan.md) — a read-only template. Per-project progress is tracked in `v9-projects/<name>/migration-status.md`.

```
Sub-Task 1     Audit v8 project — classify every asset as Migrate as-is /
               Requires manual update / Must replace. Produce migration-inventory.md.

Sub-Task 2     Migrate project structure and pom.xml — replace RHPAM BOM with
               Kogito + Quarkus BOM; delete v8-only config files; create
               application.properties skeleton.

Sub-Task 3     Migrate BPMN workflow assets — trigger XML upgrade via tooling;
               replace JavaScript scripting with Java; replace DROOLS gateway
               expressions; refactor shared KIE-session patterns; fix process IDs.

Sub-Task 4     Migrate DMN decision assets — upgrade to DMN 1.6; remove PMML
               references; recreate Java-backed types via Developer Tools.

Sub-Task 5     Migrate DRL rules, decision tables, test scenarios — convert
               Guided Rules / DSL / Scorecards to DRL or DMN; update JUnit
               activator to @TestScenarioActivator (JUnit 5).

Sub-Task 6     Migrate custom WorkItemHandlers — new API, new registration
               mechanism, remove @Wid annotations, reconfigure retry logic.

Sub-Task 7     Migrate security, auth, UserGroupCallback, AssignmentStrategy —
               WildFly/JAAS replaced by OIDC; UserGroupCallback replaced by
               IdentityProvider; AssignmentStrategy replaced by
               UserTaskAssignmentStrategy.

Sub-Task 8     Migrate forms — v8 .frm files are incompatible; regenerate all
               forms using Developer Tools "Generate form code for User Task".

Sub-Task 9     Migrate event streaming and event listeners — TaskLifeCycleEventListener
               replaced by UserTaskEventListener; Kafka reconfigured via
               mp.messaging.* / spring.kafka.* properties.

Sub-Task 10    Runtime deployment and live-data cutover — deploy v9 service;
               provision a new database (schemas are incompatible); run v8 and
               v9 in parallel; route new instances to v9; decommission v8 once
               all in-flight instances complete.
```

![Migration flow](docs/images/migration-flow.png)

### Repository layout

```
bamoe_project_migrator/
├── v8-projects/                  # Your v8 exports go here (input)
├── v9-projects/                  # Migrated v9 projects appear here (output)
│   └── <name>/
│       ├── migration-inventory.md
│       └── migration-status.md
├── v8-to-v9-migration-samples/   # Reference tutorials with working v8 + v9 pairs
├── docs/
│   ├── images/                   # README diagrams
│   ├── engineers/                # Local build / Maven repo appendix
│   └── tutorial/                 # Video script for the walkthrough
├── templates/                    # settings.xml + migration-status.md templates
├── demos/                        # Recorded demo videos
├── .devin/skills/                # Devin skills used during migration
├── bamoe-v8-to-v9-migration-plan.md   # The 10-sub-task plan (read-only template)
├── AGENTS.md                     # Devin's operating instructions
└── README.md                     # This file
```

### How the agent works

`AGENTS.md` instructs Devin to:

1. **Find and normalize the input** in `v8-projects/` (unzip, flatten nested folders, rename folders with spaces).
2. **Fetch the exact BAMOE 9.5.x doc page** for each conversion step before touching any file — every sub-task carries a Knowledge Sources table linking the authoritative `.adoc`.
3. **Run all 10 sub-tasks in order** without waiting for approval between them, recording each result in `v9-projects/<name>/migration-status.md`.
4. **Never block on the private IBM Maven repository.** On Devin web the default is Convert-only (`Build: not-run`). Set the `BAMOE_MAVEN_REPO_URL` secret to switch to Convert + verify mode (see `templates/settings.xml` and `docs/engineers/local-maven-repo.md`).
5. **Enforce 17 non-negotiable conversion rules** derived from the official upgrade guides.

### Knowledge source grounding

The base URL pattern for the official docs is:

```
https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/<section>/<file>.adoc
```

The full documentation navigation tree is at:

```
https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/nav.adoc
```

### Non-negotiable conversion rules

| Rule | v8 | v9.5 |
|---|---|---|
| Config files | `kmodule.xml`, `kie-deployment-descriptor.xml`, `persistence.xml` | **Deleted** — replaced by `application.properties` |
| Property namespace | `kieserver.*`, `drools.*`, `jbpm.*` | **Replaced** by `kogito.*` |
| Script Task language | JavaScript supported | **Java only** |
| Gateway expressions | DROOLS expressions supported | **Java expressions only** |
| BPMN + DRL session | Shared KIE session (`insert`/`retract` across boundary) | **Not supported** — use Input/Output data mapping |
| Process IDs | Hyphens and dots allowed | **Must be camelCase** (hyphens/dots break codegen) |
| PMML | Supported | **Not supported** — replace with DMN or external ML |
| Guided Rules / DSL / Scorecards | Supported | **Must convert** to DRL or DMN |
| Forms | `.frm` files | **Incompatible** — regenerate via Developer Tools |
| WIH interface | `implements WorkItemHandler` | `extends DefaultKogitoWorkItemHandler` |
| WIH lifecycle methods | `executeWorkItem` / `abortWorkItem` | `activateWorkItemHandler` / `abortWorkItemHandler` |
| WIH registration | `kie-deployment-descriptor.xml` | `@ApplicationScoped` `DefaultWorkItemHandlerConfig` bean |
| `@Wid` annotation | Used on WIH classes | **Removed** — `.wid` files kept |
| Auth / identity | WildFly JAAS, `UserGroupCallback`, LDAP | **OIDC** via `IdentityProvider` |
| Task event listener | `TaskLifeCycleEventListener` before/after callbacks | `UserTaskEventListener` single-callback `onUserTaskState` |
| Database | Shared across versions | **New DB required** — side-by-side parallel run only |
| Java packages | `javax.*` | **`jakarta.*`** |

### Architecture: before and after

```
BAMOE v8                              BAMOE v9.5
------------------------------------  ------------------------------------
Business Central (authoring +         BAMOE Canvas (business-analyst UI)
  internal Git + Maven)               BAMOE Developer Tools for VS Code
                                      External Git (GitHub / GitLab / Bitbucket)
                                      BAMOE Maven Repository (container / local)

KIE Server (KJAR deployment,          Kogito microservice embedded in
  centralised runtime)                  Quarkus 3.x or Spring Boot 3.x
                                        Deployed as container image / Uber-JAR

Smart Router (load balancing)         Kubernetes-native load balancing

Business Central Monitoring           BAMOE Management Console (Helm chart)
                                      + Data-Index GraphQL API
                                      + Prometheus / Grafana

WildFly / JBoss EAP                   Standard JVM / container runtime
JAAS / LDAP authentication            OIDC (Keycloak or any compliant IdP)
kmodule.xml + XML descriptors         pom.xml + application.properties only
Java 8 or 11 / Maven 3.6.x            Java 21 / Maven 3.9.11+
```

### Available skills

The following skills live in `.devin/skills/`:

| Skill | Purpose | Sub-Task |
|---|---|---|
| `bamoe-migrate` | One-prompt end-to-end migration (runs all sub-tasks) | All |
| `bamoe-audit-v8-project` | Audits v8 project and creates migration-inventory.md | Sub-Task 1 |
| `bamoe-configure-maven-repository` | Configures Maven to use BAMOE Maven Repository | Prerequisite |
| `bamoe-migrate-project-structure` | Migrates project structure and POM from v8 to v9 | Sub-Task 2 |
| `bamoe-migrate-bpmn` | Migrates BPMN workflow assets and upgrades XML | Sub-Task 3 |
| `bamoe-migrate-forms` | Regenerates .frm forms using Developer Tools | Sub-Task 8 |
| `bamoe-migrate-security` | Migrates security from JAAS to OIDC | Sub-Task 7 |
| `bamoe-deploy-verify` | Deploys and verifies the migrated v9 service | Sub-Task 10 |

### References

| Resource | URL |
|---|---|
| BAMOE 9.5.x documentation tree | https://github.com/IBM/bamoe-docs/blob/9.5.x/nav.adoc |
| Upgrade overview | https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/upgrading-80x-current.adoc |
| Key differences v8 vs v9 | https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/02-key-differences.adoc |
| Not supported in v9.5 | https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/11-not-supported.adoc |
| BAMOE Canvas Quarkus Accelerator | https://github.com/IBM/bamoe-canvas-quarkus-accelerator |
| Local build appendix (engineers) | [docs/engineers/local-maven-repo.md](docs/engineers/local-maven-repo.md) |
