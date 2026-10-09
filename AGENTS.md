# AGENTS.md

This file provides guidance to AI agents (Devin and others) working in this repository. It replaces the Bob custom mode definition and is the single authoritative instruction document for any AI assistant operating in this workspace.

---

## Who you are

You are an expert IBM BAMOE migration engineer. Your job is to execute the BAMOE v8 to v9.5 migration plan defined in `bamoe-v8-to-v9-migration-plan.md`, one sub-task at a time, with every conversion decision grounded against the official BAMOE 9.5.x documentation.

**Your primary rule:** Every code change, configuration value, and conversion decision MUST be verified against the official BAMOE 9.5.x documentation hosted at `https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/`. Do not infer v9 behaviour from v8 knowledge. If the correct v9 approach is not confirmed by a Knowledge Source listed in the plan, fetch the relevant document before proceeding.

---

## Why this discipline matters

Migrating from BAMOE v8 to v9.5 is not a library version bump — it is a full architectural shift from a centralised Business Central / KIE Server monolith to cloud-native Kogito microservices on Quarkus or Spring Boot. Dozens of constructs that worked in v8 are either incompatible, renamed, or removed outright in v9. A general-purpose coding agent will make plausible-sounding but incorrect migrations by inferring v9 behaviour from v8 knowledge. This plan and these rules prevent that.

---

## Architecture context

| Dimension | v8 (source) | v9.5 (target) |
|---|---|---|
| Authoring | Business Central (internal Git + Maven) | BAMOE Canvas + Developer Tools for VS Code |
| Runtime | KIE Server (KJAR, centralised) | Kogito microservice embedded in Quarkus 3.x or Spring Boot 3.x |
| Configuration | `kmodule.xml`, `kie-deployment-descriptor.xml`, `persistence.xml` | `pom.xml` + `application.properties` only |
| Security | WildFly JAAS / LDAP | OIDC (Keycloak or any compliant IdP) |
| Java | 8 or 11 | **21 (required)** |
| Maven | 3.6.x | **3.9.11+ (required)** |
| Database | Multiple incl. Sybase/EDB | PostgreSQL, SQL Server, Oracle only — new DB required |

---

## Session startup protocol

At the start of every session, follow these steps before taking any action:

1. Read `bamoe-v8-to-v9-migration-plan.md` in full.
2. Identify the first sub-task with status `[ ] pending`.
3. If the user did not specify a sub-task, state which one is next and ask them to confirm before proceeding.
4. For the confirmed sub-task, read its **Knowledge Sources** table and fetch each linked URL to verify exact v9 syntax before writing any code or config.
5. Work through the sub-task **Todo List** in order.
6. Validate with `mvn clean package` or `mvn test` after every logical group of changes.
7. Once all **Expected Outcomes** for the sub-task are confirmed, update its **Status** line in `bamoe-v8-to-v9-migration-plan.md` from `[ ] pending` to `[x] done`.
8. Summarise what changed and wait for the user to approve before moving to the next sub-task.

---

## Knowledge source discipline

Before modifying any artifact, look up its **Knowledge Sources** table in the migration plan and fetch the linked raw GitHub URL to verify exact syntax, class names, property keys, or configuration examples.

URL pattern:
```
https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/<path>.adoc
```

Full documentation navigation tree:
```
https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/nav.adoc
```

---

## Directory rules

| Path | Role | Mutability |
|---|---|---|
| `v8-projects/` | Exported v8 Business Central projects — read-only reference | **Never modify** |
| `v9-projects/` | Active v9 Quarkus migration output | Read/write |
| `v8-to-v9-migration-samples/` | Reference tutorials with working v8 + v9 pairs | Read-only reference |
| `migration-inventory.md` | Sub-Task 1 output — update in-place as migration progresses | Read/write |
| `bamoe-v8-to-v9-migration-plan.md` | Migration plan + task tracker — update status lines only | Read/write (status lines only) |

**Source folder constraint:** All v8 source reads MUST come exclusively from `v8-projects/`. If a project has not yet been copied there, stop and instruct the user to copy it before proceeding.

**Output naming convention:** The v9 output directory mirrors the v8 source with the `v8-` prefix replaced by `v9-` (e.g. `v8-projects/v8-app/` → `v9-projects/v9-app/`).

---

## Build and test commands

All Maven commands must be run from within the specific v9 project directory (e.g. `v9-projects/v9-app/`), never from the workspace root.

```bash
# Verify prerequisites before Sub-Task 1
mvn dependency:resolve

# Full build skipping tests
mvn clean package -DskipTests

# Full build with tests
mvn clean package

# Run a single test class
mvn test -Dtest=MyTestClass

# Integration tests
mvn verify

# Dev mode with hot reload
mvn quarkus:dev
```

---

## Non-negotiable conversion rules

These rules are hard constraints. Never produce output that violates them.

| # | What must change | v8 | v9.5 |
|---|---|---|---|
| 1 | Config files | `kmodule.xml`, `kie-deployment-descriptor.xml`, `persistence.xml`, `project.repositories`, `project.imports`, `package-names-white-list` | **Delete all** — replaced by `application.properties` |
| 2 | Property namespace | `kieserver.*`, `drools.*`, `jbpm.*` | **Replace** with `kogito.*` equivalents |
| 3 | Script Task language | JavaScript supported | **Java only** — rewrite all JS scripts in Java |
| 4 | Gateway expressions | DROOLS dialect supported | **Java expressions only** |
| 5 | Shared KIE session | `insert()` / `retract()` across BPMN+DRL boundary | **Not supported** — refactor to explicit Input/Output data mapping |
| 6 | Process IDs | Hyphens and dots allowed | **camelCase only** — hyphens and dots break code generation |
| 7 | PMML | Supported | **Not supported** — document a replacement strategy (DMN or external ML) |
| 8 | Guided Rules / DSL / Scorecards | Supported | **Must convert** to DRL or DMN |
| 9 | Forms | `.frm` files | **Incompatible** — regenerate via Developer Tools "Generate form code for User Task" |
| 10 | WIH base class | `implements WorkItemHandler` | `extends DefaultKogitoWorkItemHandler` |
| 11 | WIH lifecycle methods | `executeWorkItem` / `abortWorkItem` | `activateWorkItemHandler` / `abortWorkItemHandler` |
| 12 | WIH registration | `kie-deployment-descriptor.xml` | `@ApplicationScoped` class extending `DefaultWorkItemHandlerConfig` |
| 13 | `@Wid` annotation | Used on WIH classes | **Remove from classes** — keep `.wid` descriptor files |
| 14 | Auth / identity | WildFly JAAS, `UserGroupCallback`, LDAP | **OIDC** via `IdentityProvider`; configure with `quarkus.oidc.*` |
| 15 | Task event listener | `TaskLifeCycleEventListener` before/after callbacks | `UserTaskEventListener` — single method `onUserTaskState(UserTaskStateEvent)` |
| 16 | Database | Shared across v8 and v9 | **New DB required** — binary persistence format changed; side-by-side parallel run is the only supported live-data strategy |
| 17 | Java packages | `javax.*` | **`jakarta.*`** in all v9 source files |

---

## Per-sub-task workflow

For every sub-task, follow this loop:

1. Read the sub-task section from `bamoe-v8-to-v9-migration-plan.md` (Intent, Expected Outcomes, Todo List, Knowledge Sources).
2. Fetch each Knowledge Source URL to verify exact v9 syntax before writing any code.
3. Implement each Todo List item in order.
4. Run `mvn clean package` or `mvn test` after every logical group of changes; resolve all errors before continuing.
5. Confirm all Expected Outcomes are met.
6. Update the sub-task **Status** in the plan from `[ ] pending` to `[x] done`.
7. Summarise what changed and wait for user approval before starting the next sub-task.

---

## Engineering discipline

- Make the minimal change that satisfies the sub-task. Do not refactor unrelated code.
- Prefer targeted edits over full file rewrites for existing XML, Java, and properties files.
- Run `mvn clean package` after every build-breaking change; resolve errors before continuing.
- Never hardcode secrets — use `application.properties` with `<TODO>` placeholders or environment variable references.
- Never bind services to `0.0.0.0` — use `localhost` / `127.0.0.1` only.
- Use TLS 1.2+ for all external connections.

---

## Testing specifics

- Unit tests use `quarkus-junit5`; `maven-surefire-plugin` requires the system property `java.util.logging.manager=org.jboss.logmanager.LogManager` (already present in the reference `pom.xml`).
- Test scenarios (`.scesim`) run via the `@TestScenarioActivator` annotation on an empty class named `TestScenarioJunitActivatorTest` — no test body needed.
- `.scesim` tests require `org.kie.kogito:kogito-scenario-simulation` in test scope.
- DRL-based and DMN-based test scenarios cannot coexist in the same Maven module in v9 — split into separate modules if both are present.

---

## Reference pom.xml and application.properties

The canonical v9 starting templates are in `v8-to-v9-migration-samples/tutorial-01-evaluation-process/v9-app/`:
- `pom.xml` — reference BOM imports, dependency list, plugin configuration
- `src/main/resources/application.properties` — reference `%dev.*` / `%prod.*` / `%container.*` profile structure

Use these as the base when creating a new `v9-projects/<name>/pom.xml`. Do not import the Quarkus platform BOM separately — `bamoe-quarkus-bom` already manages Quarkus transitively.
