# BAMOE v9.5 Migration — Expected-Output Contract and Validation Checklist

This document defines what a completed migration must look like in `v9-projects/<name>/`,
what must be absent, which outputs depend on the v8 project's contents, and how to record
status honestly in `migration-status.md`. It is the acceptance contract for the migration
plan in `bamoe-v8-to-v9-migration-plan.md`.

Every requirement below cites the official BAMOE 9.5.x document that defines it. Do not
infer v9 behaviour from v8 knowledge or from the sample projects under
`v8-to-v9-migration-samples/` (those pin BAMOE 9.3.1 — use them for shape only).

---

## 1. Required outputs — every migrated project

These must exist in `v9-projects/<name>/` regardless of what the v8 project contained.

| Output | Requirement | Source |
|---|---|---|
| `pom.xml` | Standard `jar` packaging (no `kjar`). Imports **exactly one** BAMOE BOM matching the target framework: `com.ibm.bamoe:bamoe-quarkus-bom`, `com.ibm.bamoe:bamoe-spring-boot-bom`, or `com.ibm.bamoe:bamoe-embedded-bom`. Preserves the v8 `groupId`/`artifactId`/`version`. | [`reference-guide/maven-repository-libraries.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/reference-guide/maven-repository-libraries.adoc) — "Import only the BOM that matches framework of your Business Service project" |
| `pom.xml` build plugins | Quarkus projects: `io.quarkus.platform:quarkus-maven-plugin` with `<extensions>true</extensions>` and codegen goals (`build`, `generate-code`, `generate-code-tests`). Spring Boot projects: `org.kie.kogito:kogito-maven-plugin`. `maven-surefire-plugin` sets `java.util.logging.manager=org.jboss.logmanager.LogManager`. | [`reference-guide/maven-repository-libraries.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/reference-guide/maven-repository-libraries.adoc); accelerator `pom.xml` from the `bamoe-canvas-quarkus-accelerator` branch matching v9.5 |
| `pom.xml` mandatory capability deps | Per capability actually used: workflows → `org.jbpm:jbpm-quarkus` or `org.jbpm:jbpm-with-drools-quarkus`; decisions → `org.drools:drools-quarkus-decisions`; rules → `org.drools:drools-quarkus-rules` (Spring Boot starters per same doc). | [`reference-guide/maven-repository-libraries.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/reference-guide/maven-repository-libraries.adoc) |
| `src/main/resources/application.properties` | Only `kogito.*`, `quarkus.*` (Quarkus) or `spring.*`/`kogito.*` (Spring Boot) keys. No `kieserver.*`, `drools.*`, or `jbpm.*` keys — all deprecated in v9. Secrets as `<TODO>` placeholders or env-var references, never hardcoded. | [`upgrade/05-02-upgrading-client-server-projects.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-02-upgrading-client-server-projects.adoc) — application properties table |
| `migration-status.md` | Instantiated from `templates/migration-status.md`, with every sub-task marked `done`, `skipped (reason)`, or `partial` (see §5). | AGENTS.md; `templates/migration-status.md` |
| `migration-inventory.md` | Produced by Sub-Task 1; lists every v8 asset classified as Migrate as-is / Requires manual update / Must replace. | Plan Sub-Task 1 |
| Migrated business assets | Every migratable v8 asset (`.bpmn`, `.dmn`, `.drl`, `.wid`, decision-table `.xls`/`.xlsx`, `.scesim`) present under `src/main/resources/` (or `src/test/resources/` for `.scesim`), upgraded per Sub-Tasks 3–5. | Plan Sub-Tasks 3–5; [`upgrade/05-01-upgrading-structure-differences.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-01-upgrading-structure-differences.adoc) |

## 2. Files that must be absent

A migration is not complete while any of these remain in `v9-projects/<name>/`.

| Must NOT exist | v9 replacement | Source |
|---|---|---|
| `META-INF/kmodule.xml` | Deleted; config moves to `application.properties` | [`upgrade/05-01`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-01-upgrading-structure-differences.adoc) — "Not present" |
| `META-INF/kie-deployment-descriptor.xml` | Java + `application.properties` | same doc |
| `META-INF/persistence.xml` | `application.properties` datasource keys | same doc |
| `project.repositories` | Maven `settings.xml` | same doc |
| `project.imports` | Imports in source code / rule headers | same doc |
| `package-names-white-list` | Standard Maven/Java packaging constraints | same doc |
| `patterns.json`, `themes.json` | Developer Tools form generation; theming unsupported | same doc |
| `workitem.conf` | `.wid` + `DefaultWorkItemHandlerConfig` | same doc (Custom Tasks row) |
| `global/` directory | Code or rule headers | same doc (Global variables) |
| `*.frm` form files | Regenerated via Developer Tools | [`upgrade/11-not-supported.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/11-not-supported.adoc) |
| `*.gdst`, `*.rdrl`, `*.dsl`, `*.dslr`, scorecards, `*.pmml` | Converted to DRL / DMN; PMML removed with documented replacement | [`upgrade/11-not-supported.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/11-not-supported.adoc) |

## 3. Project-dependent outputs — required only when the v8 inventory calls for them

Check each row against `migration-inventory.md`. If the finding exists, the output is required.

| v8 finding | Required v9 output | Source |
|---|---|---|
| Custom WorkItemHandlers (`.wid` + Java) | `.wid` files retained (project root or alongside BPMN); each handler `extends org.kie.kogito.process.workitems.impl.DefaultKogitoWorkItemHandler` overriding `activateWorkItemHandler`/`abortWorkItemHandler`; one `@ApplicationScoped` class extending `org.kie.kogito.process.impl.DefaultWorkItemHandlerConfig` registering all handlers; **no `@Wid` annotations**, no `implements WorkItemHandler`. | [`upgrade/05-05-upgrading-custom-work-item-handlers.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-05-upgrading-custom-work-item-handlers.adoc) |
| User Tasks with `.frm` forms | `.frm` removed; forms regenerated via Developer Tools "Generate form code for User Task" (output under `custom-forms-dev/`); if tooling unavailable, recorded as a manual follow-up (§5) — not marked `done`. | [`tools/form-generation.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/tools/form-generation.adoc) |
| `.scesim` test scenarios | Files under `src/test/resources/`; activator class `TestScenarioJunitActivatorTest` annotated `@org.drools.scenariosimulation.backend.runner.TestScenarioActivator` (JUnit 5, empty body); `org.kie.kogito:kogito-scenario-simulation` test dep in POM. DRL-based and DMN-based scesim must not coexist in one module — split if both present. | [`upgrade/05-01`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-01-upgrading-structure-differences.adoc); [`upgrade/05-04-upgrading-individual-assets.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-04-upgrading-individual-assets.adoc) |
| XLS/XLSX decision tables | `org.drools:drools-decisiontables` dependency in POM. | [`upgrade/05-04`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-04-upgrading-individual-assets.adoc) |
| Stateful/persistent workflows | `kogito.persistence.type=jdbc` + JDBC persistence add-on + `quarkus.datasource.*` (or `spring.datasource.*`) keys; **new database** — never reuse the v8 DB. | [`upgrade/07-live-data-considerations.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/07-live-data-considerations.adoc) |
| Secured endpoints / UserGroupCallback / AssignmentStrategy | `io.quarkus:quarkus-oidc` + `quarkus.oidc.*` keys (or Spring OAuth2 resource-server); `IdentityProvider` replaces `UserGroupCallback`; `UserTaskAssignmentStrategy` replaces `AssignmentStrategy`; dev mode may use `kogito.security.auth.enabled=false`. | [`upgrade/05-08-upgrading-authentication-authorization.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-08-upgrading-authentication-authorization.adoc); [`upgrade/05-06-upgrading-user-groups-callback.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-06-upgrading-user-groups-callback.adoc) |
| Kafka emission / TaskLifeCycleEventListener / ProcessEventListener | Process-event or messaging add-on deps; `mp.messaging.*` (Quarkus) or `spring.kafka.*` keys; listeners implement `UserTaskEventListener.onUserTaskState(UserTaskStateEvent)` / v9 `ProcessEventListener`, registered via `@ApplicationScoped`. | [`upgrade/05-09-upgrading-event-streaming.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-09-upgrading-event-streaming.adoc) |
| Business calendar | `calendar.properties` migrated per doc. | [`upgrade/05-07-upgrading-business-calendar.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-07-upgrading-business-calendar.adoc) |
| Case Management (CMMN) | Converted to AdHoc/Flexible BPMN (`AdHoc=true`). | [`upgrade/05-10-upgrading-case-management-project.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-10-upgrading-case-management-project.adoc) |
| Process SVG add-on used | `META-INF/processSVG/*.svg` under `src/main/resources/` + `org.kie:kie-addons-quarkus-process-svg` dep. | [`reference-guide/maven-repository-libraries.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/reference-guide/maven-repository-libraries.adoc) |
| Domain POJOs / custom Java | Real classes under `src/main/java/` using `jakarta.*` (never `javax.*`). | AGENTS.md rule 17 |

### `src/main/java` is NOT a required artifact

Kogito generates all runtime scaffolding (`Application`, `Processes`, resources, task models)
into `target/generated-sources/kogito/` at build time. **Do not create a dummy Java class,
an `Application` class, or an empty `src/main/java/` to satisfy the contract.** The reference
`v9-app` sample ships zero hand-written main sources. `src/main/java/` is required only when
§3 demands real custom code (WIHs, listeners, POJOs, config beans).

## 4. Validation checklist

**Automated first pass:** run `tools/validate-migration.sh <v9-dir> [v8-dir]` — it executes
every `[script]` check below and prints PASS/FAIL/WARN/SKIP (report-only, exit 1 on FAIL).
**End users do not need a terminal:** they invoke this through Devin by asking "validate my
migration" or `/bamoe-migrator:bamoe-validate-v9-output` (see `skills/bamoe-validate-v9-output/`)
— the agent runs the script itself and records findings in `migration-status.md`.
The `[manual]` items require human/agent judgment and remain a deliberate step.
Items marked *(verify-mode)* apply only when `BAMOE_MAVEN_REPO_URL` is set.

### Structure & POM
- [ ] `[script]` `pom.xml` exists; packaging is `jar`; exactly one `com.ibm.bamoe` BOM imported for the chosen framework.
- [ ] `[script]` No `kjar` packaging, no `kie-maven-plugin`, no RHPAM/`org.kie.server` BOMs or deps.
- [ ] `[manual]` Java release 21 in `maven.compiler.release` (or equivalent); `jakarta.*` only in sources. *(script checks `javax.` imports; confirm release version manually)*
- [ ] `[script]` `src/main/resources/application.properties` exists; `grep -E '^(kieserver|drools|jbpm)\.'` returns nothing.
- [ ] `[script]` All §2 files confirmed absent.

### Assets
- [ ] `[script]` Every BPMN process id has no hyphens/dots; no `dialect="javascript"`; no DROOLS/MVEL expression languages. *(script also WARNs on `insert()`/`retract()` in DRL — verify the shared-session refactor manually)*
- [ ] `[manual]` Every DMN saved through v9 tooling (DMN upgraded); no PMML references. *(script catches leftover `*.pmml` files)*
- [ ] `[manual]` Guided rules/tables, DSL/DSLR, scorecards converted to DRL/DMN or listed as follow-ups. *(script catches leftover files)*
- [ ] `[script]` `.scesim` activator uses `@TestScenarioActivator` and `kogito-scenario-simulation` dep present.
- [ ] `[manual]` DRL and DMN scesim not co-located in one module.

### Code
- [ ] `[script]` WIHs: `extends DefaultKogitoWorkItemHandler`, `activate`/`abortWorkItemHandler`, `@Wid` absent, `DefaultWorkItemHandlerConfig` bean present.
- [ ] `[script]` Listeners: no `TaskLifeCycleEventListener` remains (WARN); `UserTaskEventListener` used.
- [ ] `[script]` No `UserGroupCallback` impls (WARN); OIDC configured or dev-mode documented.

### Verification
- [ ] `[manual]` *(verify-mode)* `mvn clean package -DskipTests` succeeds from inside `v9-projects/<name>/`.
- [ ] `[manual]` *(verify-mode/deploy)* `quarkus.swagger-ui.always-include=true` present; Swagger UI reachable at `http://localhost:8080/q/swagger-ui/#/` when running. — [`upgrade/05-02` "How do you know it worked?"](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-02-upgrading-client-server-projects.adoc)
- [ ] `[manual]` `migration-status.md` is complete and honest per §5.

## 5. Status recording rules

`migration-status.md` is the honest record of what actually happened — not what was planned.

- **`[x] done`** — every Expected Outcome for that sub-task is met and validated per §4.
- **`[x] skipped (reason)`** — the sub-task was not applicable (e.g. no DMN assets); reason required.
- **`[ ] partial`** — work was done but gaps remain. Any sub-task with unconverted assets or
  manual steps outstanding MUST be `partial`, never `done`.
- **Manual follow-ups / known gaps** — every `partial` (or tooling-blocked) item is listed in
  the dedicated section of `migration-status.md` with: what is incomplete, why, and the exact
  manual action needed (e.g. "regenerate 3 forms in Developer Tools", "configure OIDC
  auth-server-url", "provision new PostgreSQL instance"). Incomplete conversions are recorded,
  never hidden.
- **Build:** `not-run` (convert-only default) | `pass` | `fail`. Convert + verify runs **only**
  when `BAMOE_MAVEN_REPO_URL` is set; never stall on a missing Maven repo, never run Docker.

## 6. Environment requirements (verified against 9.5.x docs)

| Requirement | Value | Source |
|---|---|---|
| Java | **21** (IBM Semeru or Eclipse Temurin) | [`upgrade/05-01` Configuration comparison](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-01-upgrading-structure-differences.adoc) — "Maven 3.9.11+, Java 21" |
| Maven | **3.9.11+** | same |
| Framework | Quarkus 3.x or Spring Boot 3.x | same doc; [`release-notes/supported-environments.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/release-notes/supported-environments.adoc) |
| Database | PostgreSQL, SQL Server, or Oracle — **new instance required** (binary persistence format changed) | [`upgrade/07-live-data-considerations.adoc`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/07-live-data-considerations.adoc) |
| DMN | Upgraded via Developer Tools/Canvas save | [`upgrade/05-04`](https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/upgrade/05-04-upgrading-individual-assets.adoc) |

> **Known doc discrepancy:** `release-notes/supported-environments.adoc` on the 9.5.x branch
> currently publishes supported-config tables only up to BAMOE 9.2.x (Java 17 / Maven 3.9.6 /
> Quarkus 3.20). The 9.5 upgrade guide's "Maven 3.9.11+, Java 21" statement is treated as
> authoritative here; re-check `supported-environments.adoc` if a 9.5 table is published.
