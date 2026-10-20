# Video Tutorial Script — "Migrate my project" (~4 minutes)

Shot-by-shot script for the end-to-end walkthrough video. Target audience: non-engineers who have a BAMOE v8 export and nothing else.

| # | Screen (what's visible) | Action | Exact on-screen text / prompt | Narration (plain English) |
|---|---|---|---|---|
| 0 | Repo README top section ("Three steps") | Scroll slowly over the README | — | "This repository turns your old IBM BAMOE version 8 project into a new version 9.5 project — automatically. You only need to do three things." |
| 1 | GitHub web UI showing `v8-projects/` | Click **Add file → Upload files**, drag the zipped v8 project in, commit | — | "First, get your v8 project into the `v8-projects` folder. You can drag a zip straight into GitHub — or clone the repo, drop the folder in, and push." |
| 2 | Devin web app home page | Click into the repo picker, select this repository, click **New session** | — | "Now open Devin on the web, pick this repository, and start a new session." |
| 3 | Empty Devin session chat box | Type the prompt and hit Enter | `Migrate my project` | "Type exactly this: 'Migrate my project'. That's the whole instruction." |
| 4 | Devin's terminal / file view | Time-lapse: Devin unzips the file, lists `v8-projects/`, finds `pom.xml` | — | "Devin unpacks the zip, finds your project, and fixes small packaging problems — like a folder nested inside a folder — by itself." |
| 5 | `v9-projects/v9-app/migration-status.md` open | Watch rows flip from `[ ] pending` to `[x] done` / `[x] skipped` | — | "You can literally watch the progress: this file has the ten migration steps and ticks them off one by one. 'Skipped' just means that kind of file wasn't in your project." |
| 6 | Devin chat, final summary message | Scroll through the summary | (sample summary: found N processes, M forms; created `v9-projects/my-project`; things to do by hand) | "When it's finished, Devin tells you in plain words what it found, what it changed, and the few things only a person can do — like checking the regenerated forms." |
| 7 | Repo file tree at `v9-projects/v9-app/` | Open `pom.xml`, `application.properties`, a `.bpmn`, `custom-forms-dev/` | — | "Your new project lives in `v9-projects`. New Maven file, new configuration file, upgraded process diagrams, and freshly generated forms." |
| 8 | Re-run demo: a zip containing `my-app/my-app/pom.xml` | Show Devin detecting the double nesting and flattening it | — | "A common gotcha: your zip has a folder inside a folder. Devin spots that `pom.xml` is one level too deep and moves everything up automatically. If it can't, it tells you exactly what to drag where." |
| 9 | README "Common pitfalls" table | Scroll the table; zoom on the help links | — | "If anything looks odd, the README has a pitfalls table in plain English. Still stuck? Open an issue or ask your BAMOE administrator." |

## Recording checklist

- [ ] Window size: 1920×1080, browser at 100% zoom, hide bookmarks bar.
- [ ] Sample project: zip `v8-projects/v8-app` and use that zip as the demo upload.
- [ ] Blur / crop: IBM internal URLs, any names or emails in commit history, Devin account menu, secret values if the `BAMOE_MAVEN_REPO_URL` setting is shown.
- [ ] Pre-stage a second repo tab with the finished `v9-projects/` output so the ending isn't time-lapsed through the full run.
- [ ] Record narration separately; each shot is ≤ 30 seconds of screen time.
- [ ] Show `Build: not-run` in `migration-status.md` and say the line out loud: "Not-run is normal on the website — the files are still complete."
