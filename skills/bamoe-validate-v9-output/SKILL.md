---
name: bamoe-validate-v9-output
description: Validates a migrated v9 project against the expected-output contract — runs mechanical checks and guides honest status recording in migration-status.md.
---

# BAMOE Validate v9 Output

Runs `<plugin-root>/tools/validate-migration.sh` against a migrated project and turns the
results into honest `migration-status.md` updates. Invoke this before marking migration
sub-tasks `done`, or any time you want to check a `v9-projects/<name>/` output.

## Where things live

- `<plugin-root>` — the folder containing `.devin-plugin/plugin.json`, i.e. two levels above this `SKILL.md`. Holds `tools/validate-migration.sh`, `docs/migration-output-contract.md`, `templates/`, and the migration plan. Resolve these with the skill's source path; never assume they are in the current directory.
- `<work-dir>` — the user's current working directory. The project under test is `<work-dir>/v9-projects/<name>/`; its v8 source (if present) is `<work-dir>/v8-projects/<name>/`.

## Steps

1. **Locate the project.** Identify the v9 output dir in `<work-dir>/v9-projects/`. If the user named one, use it. If several exist and none was named, ask which to validate (or validate all).
2. **Run the validator** (report-only; it never writes files):
   ```bash
   bash <plugin-root>/tools/validate-migration.sh <work-dir>/v9-projects/<name> <work-dir>/v8-projects/<v8-name>
   ```
   Pass the v8 source dir as the second argument when it exists — it enables v8↔v9 asset-count comparison.
3. **Interpret results.** Exit 1 means at least one FAIL. For every FAIL and WARN, list the offending file paths to the user and map each finding back to the contract row in `docs/migration-output-contract.md`.
4. **Record honestly in `<work-dir>/v9-projects/<name>/migration-status.md`:**
   - Any FAIL or unresolved WARN affecting a sub-task → mark that sub-task `[ ] partial` (never `done`).
   - Append each finding to the **Manual follow-ups / known gaps** section: what is incomplete, why, and the exact action needed.
   - Do NOT let the script edit the status file — the agent writes it deliberately (the script is report-only).
5. **Manual items the script cannot decide** — confirm these separately before declaring `done`:
   - Semantic equivalence of rewritten scripts/gateways (JavaScript→Java, DROOLS→Java).
   - Forms actually regenerated and exercised in Developer Tools (`custom-forms-dev/` output reviewed).
   - OIDC endpoints reachable; IdP configured (not just placeholder keys).
   - New database provisioned (v8 DB must never be reused).
   - Dependency versions match the 9.5.x docs, not the 9.3.1 samples.
   - In convert+verify mode only: `mvn clean package -DskipTests` result recorded as `Build: pass`/`fail` (default is `Build: not-run`).
6. **Report a plain-language summary:** checks passed, findings, and what remains manual.

## Expected Output

- Validator output with per-check PASS/FAIL/WARN/SKIP and a summary line.
- `migration-status.md` updated: `partial` + known-gaps entries for unresolved findings; `done` only where the contract is fully satisfied.
