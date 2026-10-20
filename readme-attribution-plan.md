# README Attribution & Clarification Plan

## Top-Level Overview

The `README.md` in `bradyp19/devin-bamoe-project-migrator` was derived from the
Bob-mode repository originally authored by **Boon Tee Tan (@tanbt)**
([`boontee/bamoe_project_migrator`](https://github.com/boontee/bamoe_project_migrator)).
The changes requested by management fall into four categories:

1. **Attribution** — add a clear credit block at the top of the README acknowledging
   the original framework, author, and repository.
2. **Clarify the repo's purpose** — the opening paragraph still says "Bob mode"; it
   must say explicitly that this repo *converts* the Bob mode to Devin assets.
3. **Replace the demo section** — the current demo points to the Bob demo video and a
   file named `BAMOE Project Migrator Bob Mode Demo.mp4`; replace with a Devin
   placeholder until the Devin demo is recorded.
4. **Add per-section attribution links** — every section that was lifted verbatim from
   the original Bob repo must carry a note linking to the source file on GitHub.

No functional content (migration plan, conversion rules, knowledge source URLs,
architecture table) changes. Only prose framing, attribution, and the demo block change.

---

## Sub-Task 1 — Add Attribution Block to README.md

**Status:** `[x] done`

### Intent

Insert a prominent "Based on / Acknowledgements" section immediately after the title
so that anyone reading the README — including Devin — immediately knows this work
adapts an existing Bob-mode asset.

### Expected Outcomes

- A clearly visible attribution block appears near the top of `README.md`, before the
  workspace folder structure section.
- The block names Boon Tee Tan, links to
  [`boontee/bamoe_project_migrator`](https://github.com/boontee/bamoe_project_migrator),
  and states this repo converts the Bob mode to Devin assets.
- The opening paragraph of the README no longer says "a purpose-built Bob mode" without
  qualification — it clarifies the Devin conversion context.

### Todo List

1. Read `README.md` lines 1–10 (title + opening paragraph).
2. After the `---` separator on line 10, insert a new `## Acknowledgements` section
   with the following content:
   - Credit to Boon Tee Tan (@tanbt) as the original author of the BAMOE Project
     Migrator framework.
   - Link to the original Bob-mode repository:
     `https://github.com/boontee/bamoe_project_migrator`
   - One-sentence statement: "This repository adapts that framework for use with
     **Devin** by converting the Bob custom mode (`custom_modes.yaml`) into a
     Devin-compatible `AGENTS.md`."
3. Update the opening paragraph (lines 3–8) to replace "a purpose-built Bob mode" with
   language that makes the conversion explicit, e.g.:
   > "It pairs a structured 10-sub-task migration plan with a Devin-compatible
   > `AGENTS.md` — converted from the original Bob-mode framework by
   > [@tanbt](https://github.com/boontee) — that executes every step grounded against
   > the official BAMOE 9.5.x documentation."

### Relevant Context

- File: `README.md`, lines 1–10
- Original repo URL: `https://github.com/boontee/bamoe_project_migrator`

---

## Sub-Task 2 — Clarify the Repo Purpose in the "BAMOE Migrator — Devin" Section

**Status:** `[x] done`

### Intent

The heading at line 58 already says "BAMOE Migrator — Devin", but the body text does
not explain that this is a conversion of the original Bob mode. Add one clarifying
sentence so it is unambiguous that the work here is an *adaptation*, not an original
creation.

### Expected Outcomes

- The "BAMOE Migrator — Devin" section opens with an explicit statement that this
  Devin configuration is a conversion of the Bob mode originally created by
  [@tanbt](https://github.com/boontee/bamoe_project_migrator).
- The section links to the original Bob repo.

### Todo List

1. Read `README.md` lines 58–65 (the "BAMOE Migrator — Devin" section intro).
2. Add a blockquote or italicised note directly under the `> Instructions: AGENTS.md`
   line, e.g.:
   > *This Devin configuration is a conversion of the original Bob mode created by
   > [@tanbt](https://github.com/boontee/bamoe_project_migrator). The migration
   > framework, conversion rules, and structured plan originate from that work.*
3. Do not change any other content in this section.

### Relevant Context

- File: `README.md`, lines 58–99

---

## Sub-Task 3 — Replace the Demo Section with a Devin Placeholder

**Status:** `[x] done`

### Intent

The current demo section (lines 167–175) embeds the Bob demo YouTube thumbnail and
links to `demos/BAMOE Project Migrator Bob Mode Demo.mp4`. Replace these with a
placeholder that is honest about the current state (Devin demo not yet recorded) and
retains the original Bob demo as a reference with clear labelling.

### Expected Outcomes

- The section heading changes from "BAMOE Migrator — Live Demo" to
  "BAMOE Migrator — Demo".
- A `<!-- TODO -->` comment appears at the top of the section noting that the Devin
  demo has not yet been recorded.
- The Bob demo link is retained but clearly labelled as "Original Bob Mode Demo
  (reference)" with a note that it shows the same migration workflow.
- The `demos/` local file reference is updated or removed so the file name no longer
  says "Bob Mode Demo" (or a note is added that the filename reflects the original).

### Todo List

1. Read `README.md` lines 165–176.
2. Change the section heading to `### BAMOE Migrator — Demo`.
3. Replace the current intro paragraph and YouTube embed block with:

   ```
   <!-- TODO: Record and embed a Devin demo video here once available. -->

   > **Devin demo:** Not yet recorded.

   **Original Bob Mode Demo (reference)**

   > The demo below shows the same migration workflow (Sub-Tasks 1 and 2) running
   > in the original Bob mode by [@tanbt](https://github.com/boontee/bamoe_project_migrator).
   > It illustrates the expected agent behaviour until the Devin demo is available.

   [![BAMOE Migrator Demo (Bob Mode)](https://img.youtube.com/vi/e5pNUnvGr9Y/maxresdefault.jpg)](https://www.youtube.com/watch?v=e5pNUnvGr9Y)
   ```

4. Remove the line referencing the local `.mp4` file (or update the filename reference
   note to say it is the original Bob demo recording).

### Relevant Context

- File: `README.md`, lines 165–176
- Original demo URL: `https://www.youtube.com/watch?v=e5pNUnvGr9Y`
- Local file: `demos/BAMOE Project Migrator Bob Mode Demo.mp4`

---

## Sub-Task 4 — Add Per-Section Attribution Links for Copied Content

**Status:** `[x] done`

### Intent

Every section that was copied verbatim (or near-verbatim) from the original Bob repo
must carry a small attribution note linking to the source file in
`boontee/bamoe_project_migrator`. This satisfies the manager's requirement that "every
other section you copied from Boon Tee Tan" has a link to the original.

The sections that need attribution notes are:

| Section | README.md lines | Source file in original repo |
|---|---|---|
| "How the agent works inside a session" | 187–213 | `README.md` (Bob repo) |
| "Knowledge source grounding" | 217–233 | `README.md` (Bob repo) |
| "Non-negotiable conversion rules" table | 235–258 | `.bob/custom_modes.yaml` → `roleDefinition` |
| "Architecture: before and after" | 261–285 | `README.md` (Bob repo) |

### Expected Outcomes

- Each of the four sections above contains a small italic attribution line such as:
  > *Adapted from [`boontee/bamoe_project_migrator`](https://github.com/boontee/bamoe_project_migrator)*
- The attribution line appears as the last line of each section, just before the `---`
  separator.
- No content is removed or reworded — only the attribution note is added.

### Todo List

1. Read `README.md` lines 187–290 to confirm exact section boundaries.
2. For each of the four sections, append an attribution note immediately before the
   `---` closing separator:
   ```
   *Adapted from [boontee/bamoe_project_migrator](https://github.com/boontee/bamoe_project_migrator)*
   ```
3. Verify all four attribution notes appear and link correctly.

### Relevant Context

- File: `README.md`
- Original repo: `https://github.com/boontee/bamoe_project_migrator`

---

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Attribution placement | Top of README as `## Acknowledgements` + per-section notes | Satisfies manager's "clear reference" requirement at two levels: global and per-section |
| Bob demo handling | Retain with clear "reference" label, add Devin TODO | Honest about current state; does not delete useful reference material |
| Original repo URL | `https://github.com/boontee/bamoe_project_migrator` | Confirmed by user as the correct public URL |
| Content changes | Framing and attribution only — no migration content changes | Minimal change; the migration framework itself is not altered |
