# Tutorial Index — v8 construct → local reference tutorial

Use during Sub-Task 1 and whenever a sub-task needs a worked v8→v9 example. All paths are
relative to `v8-to-v9-migration-samples/` and work offline. Each tutorial has a `README.md`,
a `v8-app/` and a `v9-app/`. Conversion rules themselves live in `AGENTS.md`; this file only
says *where to look*.

| v8 construct found in audit | Tutorial | What the v9 app shows |
|---|---|---|
| Any project (baseline) | `tutorial-01-evaluation-process` | Minimal kjar → Quarkus project; reference `pom.xml` / `application.properties` |
| Any project (baseline) | `tutorial-04-upgrade-guide-scenarios` | javax→jakarta, process ID rename, Variable Context removal, raw `List`, boolean getters, rule units |
| Any project (baseline) | `tutorial-13-common-issues` | README-only catalogue of 18 build/runtime errors with fixes; grep error text here first |
| BPMN + user tasks, `.frm` forms | `tutorial-01-evaluation-process` | Forms dropped; tasks driven via REST |
| BPMN + DRL via `ruleflow-group`, `insert()`/`retract()` in rules, `.gdst` guided decision tables | `tutorial-02-mortgage-application` | GDST → DRL; rules rewritten without `insert`/`retract`; `ruleflow-group` kept |
| DMN + `.scesim` test scenarios | `tutorial-03-traffic-violation` | DMN moved to resource root; `.scesim` run via `TestScenarioJunitActivatorTest` |
| Process / task / rule event listeners | `tutorial-05-event-listeners` | `ProcessEventLogger`, `UserTaskEventLogger`, `RuleEventLogger`, `*EventListenerConfig` registration |
| `persistence.xml`, JPA process variables | `tutorial-06-process-variable-persistence` | `jakarta.persistence` entities; Quarkus datasource + Hibernate ORM properties |
| Task deadlines, reassignment, SLA, custom assignment | `tutorial-07-human-task-escalation` | `NotStarted*`/`NotCompleted*` deadlines; User Task Subsystem REST API |
| Email notification on task deadlines | `tutorial-08-email-notifications` | `NotStartedNotify`/`NotCompletedNotify` + mail config in `application.properties` |
| Entity graphs with relationships, `javax.validation` | `tutorial-09-complex-data-models` | `jakarta.validation`; relationship mapping under Hibernate ORM |
| Maven multi-module / parent POM | `tutorial-10-multi-module` | Parent POM, kjar→jar module, service module depending on it |
| `UserGroupCallback`, LDAP/JAAS, task assignment by identity | `tutorial-11-usergroupcallback-security` | `CustomIdentityProvider` (`@Alternative`), `CustomUserTaskAssignmentStrategy`, request filter |
| Custom `WorkItemHandler`, datasource props, async jobs | `tutorial-12-database-integration` | `DatabaseWorkItemHandler` + `*WorkItemHandlerConfig`; Quarkus datasource; Jobs Service |
| Case Management (`adHoc="true"`, stages, milestones) | `tutorial-14-case-management-it-orders` | Ad-hoc case redesigned as structured BPMN; no case runtime in v9 |

Not covered by any tutorial (handle per `AGENTS.md` rules and the `upgrade/11-not-supported.adoc` doc):
PMML, DSL/DSLR, scorecards, JavaScript Script Tasks, DROOLS-dialect gateway expressions, Spring Boot target.

Note: `tutorial-05-event-listeners/` contains a stray nested copy of `tutorial-07-human-task-escalation/`; ignore it.
