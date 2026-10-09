# Devin Migration Plan — BAMOE Migrator Mode

## Top-Level Overview

This plan translates the **BAMOE Migrator Bob mode** (defined in `.bob/custom_modes.yaml`) into a
Devin-compatible instruction set, then publishes a new clean public GitHub repository that customers
can use with Devin instead of Bob.

The goal is behavioural equivalence: a customer using Devin should get the same guided, doc-grounded,
rule-enforcing migration experience that the Bob mode provides — without any Bob tooling in the repo.

**What changes:**
- `.bob/custom_modes.yaml` → replaced by a rich `AGENTS.md` at the repo root
- `.bob/rules-agent/`, `.bob/rules-ask/`, `.bob/rules-plan/` → removed (Bob mode-routing, not needed)
- `README.md` → updated to remove Bob-specific Quick Start and replace with Devin instructions
- A new public GitHub repo is created and populated

**What stays identical:**
- `bamoe-v8-to-v9-migration-plan.md` — the structured 11 sub-task migration plan; Devin reads it directly
- `v8-to-v9-migration-samples/` — all 14 reference tutorials
- `v8-projects/` and `v9-projects/` folder structure
- `migration-inventory.md`

**Non-goals:**
- No functional changes to the migration plan itself
- No changes to tutorial content
- No new migration sub-tasks added

---

## Sub-Task 1 — Author the Devin-Compatible AGENTS.md

**Status:** `[ ] pending`

### Intent

Devin's entire "mode" is its `AGENTS.md`. This is the single document that replaces
`.bob/custom_modes.yaml`. It must encode:

1. **The persona** — who Devin is acting as and its primary rule (every decision grounded against live docs)
2. **Architecture context** — what changed between v8 and v9, in concrete terms
3. **Session startup protocol** — exactly what to do at the start of every Devin session (equivalent to `customInstructions`)
4. **Knowledge source discipline** — fetch the exact `raw.githubusercontent.com` URL before modifying any artifact
5. **All 15 non-negotiable conversion rules** — verbatim from `roleDefinition` in `custom_modes.yaml`
6. **Per-sub-task workflow** — the 5-step loop: read plan → fetch docs → implement → validate → wait for approval
7. **Directory constraints** — `v8-projects/` is read-only; all writes go to `v9-projects/`
8. **Build commands** — Maven commands and the requirement to run from the v9 project subdirectory

The key difference from the existing `AGENTS.md` (created for Bob) is that this version must be fully
self-contained — no skill loading, no mode switching, no subagent spawning. Everything Devin needs
must be in the document itself.

### Expected Outcomes
- A new `AGENTS.md` at the repo root that fully replaces `.bob/custom_modes.yaml`
- A reader (human or Devin) can follow it without any knowledge of Bob
- All 15 conversion rules are present and unambiguous
- The session startup protocol is explicit: read plan → identify first pending sub-task → confirm with user
- Knowledge source URLs follow the pattern `https://raw.githubusercontent.com/IBM/bamoe-docs/9.5.x/<path>.adoc`

### Todo List
1. Read the `roleDefinition` field from `.bob/custom_modes.yaml` in full.
2. Read the `customInstructions` field from `.bob/custom_modes.yaml` in full.
3. Write a new `AGENTS.md` at the repo root using the structure:
   - Header + purpose statement
   - Persona and primary rule
   - Architecture context table (v8 vs v9)
   - Session startup protocol (numbered steps)
   - Knowledge source discipline (URL pattern + nav tree link)
   - Directory rules table
   - Build/test commands
   - All 15 non-negotiable conversion rules (bulleted, each with v8 → v9 mapping)
   - Per-sub-task workflow (the 5-step loop)
4. Verify every rule from `custom_modes.yaml` `KEY CONVERSION RULES` section appears in the new `AGENTS.md`.
5. Verify the session startup instruction ("read plan, find first pending sub-task, ask user to confirm") is present.

### Relevant Context
- Source: `.bob/custom_modes.yaml` — `roleDefinition` and `customInstructions` fields
- Current partial `AGENTS.md` at repo root exists but is Bob-mode-aware and incomplete for Devin use
- Devin reads `AGENTS.md` as a flat document; there is no mechanism for skill loading or mode switching

---

## Sub-Task 2 — Update README.md for Devin

**Status:** `[ ] pending`

### Intent

The current `README.md` has a "BAMOE Migrator — Bob Mode" section with Bob-specific quick start
instructions (VS Code, Bob chat panel, mode picker). These must be replaced with Devin-equivalent
instructions. The architectural description, migration plan overview, non-negotiable rules table, and
demo section are all tool-agnostic and stay unchanged.

### Expected Outcomes
- "BAMOE Migrator — Bob Mode" section heading and Bob-specific content replaced with "BAMOE Migrator — Devin"
- Quick start steps updated to: connect repo to Devin, open a session, type the first prompt
- "Mode capabilities" table replaced with a Devin capabilities table (web browsing, file read/write, shell)
- "How the mode works inside a session" flow diagram updated to reference `AGENTS.md` instead of `custom_modes.yaml`
- "Knowledge source grounding" section retained as-is (URLs are tool-agnostic)
- No changes to: Top-level overview, folder structure table, migration plan overview, architecture before/after, references

### Todo List
1. Read `README.md` in full; identify every Bob-specific sentence or section.
2. Replace the "BAMOE Migrator — Bob Mode" quick start with Devin equivalent steps.
3. Replace the "Mode capabilities" table with a Devin-oriented equivalent.
4. Update the "How the mode works inside a session" prose to reference `AGENTS.md`.
5. Remove any mention of VS Code mode picker, Bob chat panel, or `custom_modes.yaml`.
6. Retain the demo video section, architecture table, non-negotiable rules table, and references unchanged.

### Relevant Context
- `README.md` lines 58–218 are the Bob-specific section to rewrite
- Lines 1–57 (workspace structure) and lines 239–303 (architecture + references) are unchanged

---

## Sub-Task 3 — Strip Bob-Specific Files

**Status:** `[ ] pending`

### Intent

Remove all files that are Bob machinery and have no meaning in a Devin context. The `.bob/` directory
(excluding `custom_modes.yaml` which is now superseded by `AGENTS.md`) should be removed. The
mode-specific `AGENTS.md` files inside `.bob/rules-*/` are Bob routing files, not Devin instructions.

### Expected Outcomes
- `.bob/` directory entirely absent from the new repo
- No references to `custom_modes.yaml`, Bob mode slugs, or `.bob/` paths remain in any file
- `AGENTS.md` at repo root is the sole instruction document

### Todo List
1. Confirm the new `AGENTS.md` (Sub-Task 1) is complete before deleting anything.
2. Mark `.bob/` for exclusion when populating the new repo (do not copy it).
3. Search all Markdown files for remaining references to `.bob/`, `custom_modes.yaml`, or "Bob mode" and update them.

### Relevant Context
- Files to exclude: `.bob/custom_modes.yaml`, `.bob/rules-agent/AGENTS.md`, `.bob/rules-ask/AGENTS.md`, `.bob/rules-plan/AGENTS.md`
- The `AGENTS.md` files in `.bob/rules-*/` were created for Bob mode routing and are not Devin instructions

---

## Sub-Task 4 — Create and Populate the New Public GitHub Repo

**Status:** `[ ] pending`

### Intent

Create a new public GitHub repository and push the cleaned content into it. The repo should be
immediately usable by a customer who clones it and connects it to Devin.

### Expected Outcomes
- A new public GitHub repo exists (owner and name TBD with user)
- Contents mirror this workspace minus `.bob/` and minus the current Bob-oriented `README.md` and `AGENTS.md`
- The new Devin `AGENTS.md` and updated `README.md` are present at the root
- `v8-projects/` contains only `.gitkeep` (customers bring their own v8 project)
- `v9-projects/` contains only `.gitkeep` (output directory; starts empty)
- `migration-inventory.md` is reset to a blank template (current one is specific to the demo v8-app project)
- `v8-to-v9-migration-samples/` is present in full (reference tutorials)
- `bamoe-v8-to-v9-migration-plan.md` is present with all sub-task statuses reset to `[ ] pending`

### Todo List
1. Confirm GitHub org/user and repo name with the user before creating anything.
2. Create the new public GitHub repo via the GitHub API.
3. Push files in this order:
   a. `AGENTS.md` (new Devin version)
   b. `README.md` (updated version)
   c. `bamoe-v8-to-v9-migration-plan.md` (all sub-task statuses reset to `[ ] pending`)
   d. `v8-to-v9-migration-samples/` (all tutorial subdirectories)
   e. `v8-projects/.gitkeep`
   f. `v9-projects/.gitkeep`
   g. `docs/.gitkeep`
   h. `demos/.gitkeep`
   i. A blank `migration-inventory.md` template
4. Verify the repo is public and the root `AGENTS.md` is visible.
5. Share the repo URL with the user.

### Relevant Context
- **Target repo:** `bradyp19/devin-bamoe-project-migrator` (public)
- Use `mcp__github__create_repository` with `private: false` under owner `bradyp19`
- Use `mcp__github__push_files` for the initial content push
- `bamoe-v8-to-v9-migration-plan.md` has Sub-Tasks 1 and 2 marked `[x] done` in this working repo — reset **all** sub-task statuses to `[ ] pending` in the customer copy (every customer starts from scratch with their own v8 project)
- `migration-inventory.md` currently contains the specific audit of the demo `v8-app` project — replace with a blank template that shows the expected structure

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Single `AGENTS.md` vs multiple | Single file at repo root | Devin has no mode-routing; one flat document is simpler and reliable |
| Live doc fetching vs embedded content | Live fetch retained | Devin has web browsing; live fetching ensures correct v9 syntax, same as Bob mode |
| Bob files in new repo | Excluded entirely | No Bob tooling in a Devin-targeted repo; avoids confusion |
| Plan file structure | Unchanged | Devin reads it directly; the sub-task structure is the workflow |
| Sub-task statuses in new repo | All reset to pending | Customers start from the beginning; demo-completed statuses would confuse them |
