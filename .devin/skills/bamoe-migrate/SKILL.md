---
name: bamoe-migrate
description: End-to-end BAMOE v8 → v9.5 migration of whatever is in v8-projects/ — run this when the user says "migrate my project" or similar
---

# BAMOE Migrate (End-to-End)

Runs the complete BAMOE v8 → v9.5 migration on whatever project is in `v8-projects/`, following the run-through protocol in `AGENTS.md`. Invoke this when the user says "migrate my project" or asks for the whole migration in one go.

## Build mode rule

- **Convert-only (default):** no Maven needed. Perform all file conversions and record `Build: not-run` in `migration-status.md`. Never block or stall on a missing Maven repository; never try to run Docker.
- **Convert + verify:** only if `BAMOE_MAVEN_REPO_URL` is set. Write `~/.m2/settings.xml` from `templates/settings.xml`, run `mvn clean package -DskipTests` inside the v9 project, and record `pass`/`fail`.

## Steps

1. **Find the input.** Look in `v8-projects/`.
   - A `*.zip` → unzip into a folder named after the zip's basename, delete the zip.
   - `v8-projects/X/X/pom.xml` (nested one level too deep) → move contents up one level.
   - Folder name has spaces → rename with hyphens.
   - No `pom.xml` anywhere under `v8-projects/` → stop and tell the user in plain words what a v8 export must contain (point them to README "What goes in").
   - Multiple projects → ask one question: which one (or all).
2. **Create the output.** Output dir = `v9-projects/<name>` — the v8 folder name with `v8-` replaced by `v9-`; if there is no `v8-` prefix, keep the same name. Create `v9-projects/<name>/migration-status.md` from `templates/migration-status.md`.
3. **Run Sub-Tasks 1→10 in order**, WITHOUT waiting for approval between sub-tasks. For each sub-task, read its section of `bamoe-v8-to-v9-migration-plan.md` (Intent, Expected Outcomes, Todo List, Knowledge Sources) and fetch the linked doc pages before writing code. Mark each `[x] done` or `[x] skipped (reason)` in the per-project `migration-status.md` — never in the plan file.
   - Sub-Task 1 → use the `bamoe-audit-v8-project` skill.
   - Sub-Task 2 → use the `bamoe-migrate-project-structure` skill.
   - Sub-Task 3 → use the `bamoe-migrate-bpmn` skill.
   - Sub-Tasks 4, 5, 6, 9 → follow the plan's sub-task sections directly.
   - Sub-Task 7 → use the `bamoe-migrate-security` skill.
   - Sub-Task 8 → use the `bamoe-migrate-forms` skill.
   - Sub-Task 10 → use the `bamoe-deploy-verify` skill.
   Only stop to ask when: the input is ambiguous; an asset is unsupported in v9 with no automatic replacement (PMML, scorecards needing business input); or something destructive would be needed. Phrase every question for a non-engineer with 2–3 options.
4. **Finish with a plain-language summary:** what was found, what changed, what the user must do by hand (e.g. opening regenerated forms in BAMOE Developer Tools), and where the output is (`v9-projects/<name>/`).
