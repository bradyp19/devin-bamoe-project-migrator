export type Shot = {
  id: number;
  kind: 'synthetic' | 'footage';
  durationSec: number;
  caption: string;
  rawFile?: string;
  screen?: string;
  action?: string;
};

export const FPS = 30;
export const TRANSITION_FRAMES = 15;

export const shots: Shot[] = [
  {
    id: 0,
    kind: 'synthetic',
    durationSec: 8,
    caption:
      'This repository turns your old IBM BAMOE version 8 project into a new version 9.5 project — automatically. You only need to do three things.',
  },
  {
    id: 1,
    kind: 'synthetic',
    durationSec: 15,
    caption:
      'First, get your v8 project into the `v8-projects` folder. You can drag a zip straight into GitHub — or clone the repo, drop the folder in, and push.',
  },
  {
    id: 2,
    kind: 'synthetic',
    durationSec: 10,
    caption:
      'Now open Devin on the web, pick this repository, and start a new session.',
  },
  {
    id: 3,
    kind: 'footage',
    durationSec: 8,
    rawFile: 'raw/shot-03.mp4',
    screen: 'Empty Devin session chat box',
    action: "Type the prompt 'Migrate my project' and hit Enter",
    caption: "Type exactly this: 'Migrate my project'. That's the whole instruction.",
  },
  {
    id: 4,
    kind: 'footage',
    durationSec: 20,
    rawFile: 'raw/shot-04.mp4',
    screen: "Devin's terminal / file view",
    action:
      'Time-lapse: Devin unzips the file, lists v8-projects/, finds pom.xml',
    caption:
      'Devin unpacks the zip, finds your project, and fixes small packaging problems — like a folder nested inside a folder — by itself.',
  },
  {
    id: 5,
    kind: 'footage',
    durationSec: 20,
    rawFile: 'raw/shot-05.mp4',
    screen: 'v9-projects/v9-app/migration-status.md open',
    action:
      'Watch rows flip from [ ] pending to [x] done / [x] skipped',
    caption:
      "You can literally watch the progress: this file has the ten migration steps and ticks them off one by one. 'Skipped' just means that kind of file wasn't in your project.",
  },
  {
    id: 6,
    kind: 'footage',
    durationSec: 15,
    rawFile: 'raw/shot-06.mp4',
    screen: 'Devin chat, final summary message',
    action: 'Scroll through the summary',
    caption:
      "When it's finished, Devin tells you in plain words what it found, what it changed, and the few things only a person can do — like checking the regenerated forms.",
  },
  {
    id: 7,
    kind: 'synthetic',
    durationSec: 15,
    caption:
      'Your new project lives in `v9-projects`. New Maven file, new configuration file, upgraded process diagrams, and freshly generated forms.',
  },
  {
    id: 8,
    kind: 'synthetic',
    durationSec: 20,
    caption:
      "A common gotcha: your zip has a folder inside a folder. Devin spots that `pom.xml` is one level too deep and moves everything up automatically. If it can't, it tells you exactly what to drag where.",
  },
  {
    id: 9,
    kind: 'synthetic',
    durationSec: 10,
    caption:
      'If anything looks odd, the README has a pitfalls table in plain English. Still stuck? Open an issue or ask your BAMOE administrator.',
  },
];

export const totalDurationFrames =
  shots.reduce((sum, s) => sum + s.durationSec, 0) * FPS;
