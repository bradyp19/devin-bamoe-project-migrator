# Tutorial video (Remotion)

Renders the ~2.5 minute tutorial defined in `../video-script.md` as a fully
programmatic video: every shot is an animated "synthetic" component, including
shots 3–6, which simulate the Devin web UI (see below).

**Rendered video:** [https://youtu.be/hioFbZQwGvo](https://youtu.be/hioFbZQwGvo)

## Requirements

- Node.js 18+

## Install

```bash
npm install
```

## Preview (Remotion Studio)

```bash
npm run dev
```

Opens Remotion Studio in your browser — scrub through the `BamoeMigratorTutorial`
composition (1920×1080, 30 fps, 4230 frames / 141 s).

## Render

```bash
npm run build
```

Writes `out/tutorial.mp4` (H.264, 1920×1080, 30 fps).

## Shots 3–6: simulated Devin UI

Shots 3–6 were originally planned as real screen recordings. They are now
**simulated in Remotion** — synthetic components that mimic the Devin web UI,
matching the style of the other animated shots:

| Shot | Component | What it shows |
|---|---|---|
| 3 | `src/shots/TypePrompt.tsx` | Chat input typing `Migrate my project`, send, message bubble |
| 4 | `src/shots/DevinTerminal.tsx` | Time-lapse terminal: unzip, `ls v8-projects/`, `find pom.xml` |
| 5 | `src/shots/StatusTable.tsx` | `migration-status.md` rows flipping `[ ] pending` → `[x] done` / `[x] skipped` |
| 6 | `src/shots/FinalSummary.tsx` | Assistant summary bubble revealing what was found/changed and manual follow-ups |

**Real-footage fallback:** the `Footage` component and `public/raw/` mechanism
are still in place. To swap a real recording back in, set the shot's
`kind: 'footage'` and `rawFile: 'raw/shot-0N.mp4'` in `src/script.ts` and drop
the file into `public/raw/` — missing files render a "Recording pending" card
instead of crashing.

## Preview

Still frames from the synthetic shots (in `preview/`):

| Shot | Preview |
|---|---|
| 1 — upload to `v8-projects/` | ![upload](preview/shot-01-upload.png) |
| 7 — the "What comes out" tree | ![tree](preview/shot-07-tree.png) |
| 8 — nested-folder self-fix | ![nested](preview/shot-08-nested.png) |

## Layout

```
src/script.ts     shot list data (id, kind, duration, caption, rawFile)
src/Root.tsx      composition: TransitionSeries + 15-frame cross-fades
src/style.ts      shared colours / fonts
src/shots/        one component per shot + shared Caption subtitle bar
public/raw/       real screen recordings go here
```
