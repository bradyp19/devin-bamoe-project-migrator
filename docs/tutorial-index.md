# Tutorial Index — v8 construct → local reference tutorial

Use during Sub-Task 1 and whenever a sub-task needs a worked v8→v9 example. All paths are
relative to `v8-to-v9-migration-samples/` and work offline. Each tutorial has a `README.md`,
a `v8-app/` and a `v9-app/`. Conversion rules themselves live in `AGENTS.md`; this file only
says *where to look*.

All samples pin BAMOE 9.3.1 / Java 17 — copy structure, not versions or property keys. Where a
README and the shipped code disagree, the **Caveat** column says so; trust the code.

| v8 construct found in audit | Tutorial | What the v9 app shows | Caveat |
|---|---|---|---|
| Any project (baseline) | `tutorial-01-evaluation-process` | Minimal kjar → Quarkus project; reference `pom.xml` / `application.properties` | v9 `evaluation.bpmn` is byte-identical to v8 (still `#{employee}` single-owner); README's "package fix" never applied |
| Any project (baseline) | `tutorial-04-upgrade-guide-scenarios` | javax→jakarta, process ID rename, raw `List`, boolean getters, rule units | README claims 11 scenarios, ships 9; "context→kcontext" scenario is fictional (v8 already used `kcontext`); still ships `kmodule.xml` |
| Any project (baseline) | `tutorial-13-common-issues` | README-only catalogue of 18 build/runtime errors with fixes; grep error text here first | Issue numbering has gaps; PIM section is v9→v9 only, not a v8 cutover tool |
| BPMN + user tasks, `.frm` forms | `tutorial-01-evaluation-process` | Forms dropped; tasks driven via REST | see above |
| BPMN + DRL via `ruleflow-group`, `insert()`/`retract()` in rules, `.gdst` guided decision tables | `tutorial-02-mortgage-application` | GDST → DRL; rules rewritten without `insert`/`retract`; `ruleflow-group` kept | README's `KieFunctions` gateway issue is fictional; real fix was null-safe Java condition |
| DMN + `.scesim` test scenarios | `tutorial-03-traffic-violation` | DMN moved to resource root; `.scesim` run via `TestScenarioJunitActivatorTest` | README says add `quarkus-jdbc-h2`; service is stateless, has no datasource |
| Process / task / rule event listeners | `tutorial-05-event-listeners` | `ProcessEventLogger`, `UserTaskEventLogger`, `RuleEventLogger`, `*EventListenerConfig` registration | v9 has no DRL, so rule listeners never fire; contains stray nested copy of tutorial-07 |
| `persistence.xml`, JPA process variables | `tutorial-06-process-variable-persistence` | `jakarta.persistence` entities; Quarkus datasource + Hibernate ORM properties | README property table does not match shipped `application.properties`; follow the file |
| Task deadlines, reassignment, SLA, custom assignment | `tutorial-07-human-task-escalation` | `NotStarted*`/`NotCompleted*` deadlines; User Task Subsystem REST API | Lowercase `readme.md`; assignment strategy returns users not defined in properties |
| Email notification on task deadlines | `tutorial-08-email-notifications` | `NotStartedNotify`/`NotCompletedNotify` + mail config in `application.properties` | **No v9 Java at all** — listener exists only as README snippet; README itself says feature is broken on the pinned 9.3.1 |
| Entity graphs with relationships, `javax.validation` | `tutorial-09-complex-data-models` | `jakarta.validation`; relationship mapping under Hibernate ORM | No v8 BPMN; README's Serializable / `serialVersionUID` issues are fictional (already present) |
| Maven multi-module / parent POM | `tutorial-10-multi-module` | Parent POM, kjar→jar module, service module depending on it | Parent pom lists Maven Central only — needs BAMOE repo profile; README names classes that don't exist |
| `UserGroupCallback`, LDAP/JAAS, task assignment by identity | `tutorial-11-usergroupcallback-security` | `CustomIdentityProvider` (`@Alternative`), `CustomUserTaskAssignmentStrategy`, request filter | **Do not copy `UserContextFilter`**: it takes groups from the caller's query params, so the 403 check can never fail. Wiring pattern only |
| Custom `WorkItemHandler`, datasource props, async jobs | `tutorial-12-database-integration` | `DatabaseWorkItemHandler` + `*WorkItemHandlerConfig`; Quarkus datasource; Jobs Service | BPMN identical v8→v9; process id `database-process` violates the no-hyphen rule |
| Case Management (`adHoc="true"`, stages, milestones) | `tutorial-14-case-management-it-orders` | Ad-hoc case redesigned as structured BPMN; no case runtime in v9 | `place-order.bpmn` has `process id="place_order"` but `bpmnElement="place-order"` (the mismatch its README warns about); v8 export has many zero-byte files |

Not covered by any tutorial (handle per `AGENTS.md` rules and the `upgrade/11-not-supported.adoc` doc):
PMML, DSL/DSLR, scorecards, JavaScript Script Tasks, DROOLS-dialect gateway expressions, Spring Boot target.
