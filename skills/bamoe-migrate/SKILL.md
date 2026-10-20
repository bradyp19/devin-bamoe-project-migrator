---
name: bamoe-migrate
description: End-to-end BAMOE v8 → v9.5 migration of a v8 Business Central export — run this when the user says "migrate my project" or similar
---

# BAMOE Migrate (End-to-End)

Runs the complete BAMOE v8 → v9.5 migration on a v8 Business Central export, following the steps below. Invoke this when the user says "migrate my project" or asks for the whole migration in one go.

## Where things live

- `<plugin-root>` — the folder containing `.devin-plugin/plugin.json`, i.e. two levels above this `SKILL.md`. Holds `bamoe-v8-to-v9-migration-plan.md`, `templates/`, `v8-to-v9-migration-samples/`, and `docs/tutorial-index.md`. Resolve these with the skill's source path; never assume they are in the current directory.
- `<work-dir>` — the user's current working directory. Input is `<work-dir>/v8-projects/<name>/`, or a path the user named explicitly; output is always `<work-dir>/v9-projects/<name>/`.
- When this plugin repo itself is the working directory, the two are the same folder.

## Build mode rule

- **Convert-only (default):** no Maven needed. Perform all file conversions and record `Build: not-run` in `migration-status.md`. Never block or stall on a missing Maven repository; never try to run Docker.
- **Convert + verify:** only if `BAMOE_MAVEN_REPO_URL` is set. Write `~/.m2/settings.xml` from `<plugin-root>/templates/settings.xml`, run `mvn clean package -DskipTests` inside the v9 project, and record `pass`/`fail`.

## Steps

1. **Find the input.** If the user named a folder or .zip, use that path. Otherwise look in `<work-dir>/v8-projects/`.
   - A `*.zip` → unzip into a folder named after the zip's basename, delete the zip.
   - `X/X/pom.xml` (nested one level too deep) → move contents up one level.
   - Folder name has spaces → rename with hyphens.
   - No `pom.xml` anywhere → stop and tell the user in plain words what a v8 export must contain: a `pom.xml` at the top level and `src/main/resources/` holding the BPMN/DMN/DRL assets plus `META-INF/kmodule.xml`.
   - Multiple projects → ask one question: which one (or all).
2. **Create the output.** Output dir = `<work-dir>/v9-projects/<name>` — the v8 folder name with `v8-` replaced by `v9-`; if there is no `v8-` prefix, keep the same name. Create `<work-dir>/v9-projects/<name>/migration-status.md` from `<plugin-root>/templates/migration-status.md`.
3. **Run Sub-Tasks 1→10 in order**, WITHOUT waiting for approval between sub-tasks. For each sub-task, read its section of `<plugin-root>/bamoe-v8-to-v9-migration-plan.md` (Intent, Expected Outcomes, Todo List, Knowledge Sources) and fetch the linked doc pages before writing code. Mark each `[x] done` or `[x] skipped (reason)` in the per-project `migration-status.md` — never in the plan file.
   - Sub-Task 1 → use the `bamoe-audit-v8-project` skill.
   - Sub-Task 2 → use the `bamoe-migrate-project-structure` skill.
   - Sub-Task 3 → use the `bamoe-migrate-bpmn` skill.
   - Sub-Tasks 4, 5, 6, 9 → follow the plan's sub-task sections directly.
   - Sub-Task 7 → use the `bamoe-migrate-security` skill.
   - Sub-Task 8 → use the `bamoe-migrate-forms` skill.
   - Sub-Task 10 → use the `bamoe-deploy-verify` skill.
   Only stop to ask when: the input is ambiguous; an asset is unsupported in v9 with no automatic replacement (PMML, scorecards needing business input); or something destructive would be needed. Phrase every question for a non-engineer with 2–3 options.
4. **Finish with a plain-language summary:** what was found, what changed, what the user must do by hand (e.g. opening regenerated forms in BAMOE Developer Tools), and where the output is (`<work-dir>/v9-projects/<name>/`).

## Per-sub-task loop

For every sub-task:
1. Read its section of `<plugin-root>/bamoe-v8-to-v9-migration-plan.md` (Intent, Expected Outcomes, Todo List, Knowledge Sources).
2. Fetch each Knowledge Source URL (`https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/<path>.adoc`) to verify exact v9 syntax before writing any code.
3. Implement each Todo List item in order, in `<work-dir>/v9-projects/<name>/`.
4. In Convert + verify mode, run `mvn clean package -DskipTests` from inside the v9 project directory (never from the workspace root) after each logical group of changes; resolve errors before continuing. In Convert-only mode skip this.
5. Confirm all Expected Outcomes are met, then update that sub-task's line in `migration-status.md` to `[x] done` or `[x] skipped (reason)` and move straight on.
