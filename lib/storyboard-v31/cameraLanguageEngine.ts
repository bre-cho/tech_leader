import type { ShotSpec } from "./types";

function cameraClass(shot: ShotSpec) {
  const text = `${shot.camera} ${shot.lens} ${shot.title}`.toLowerCase();
  if (/macro|insert|detail/.test(text)) return "macro";
  if (/close|face|eye|portrait/.test(text)) return "close";
  if (/medium/.test(text)) return "medium";
  if (/wide|establishing|flycam/.test(text)) return "wide";
  if (/telephoto|runway/.test(text)) return "telephoto";
  return "medium";
}

export function analyzeCameraLanguage(shots: ShotSpec[]) {
  const classes = shots.map(s => ({ shotId: s.id, class: cameraClass(s) }));
  const badRuns: Array<{ startShot: number; endShot: number; class: string; length: number }> = [];
  let runStart = 0;

  for (let i = 1; i <= classes.length; i++) {
    if (i === classes.length || classes[i].class !== classes[runStart].class) {
      const length = i - runStart;
      if (length >= 4 && ["macro", "close", "wide"].includes(classes[runStart].class)) {
        badRuns.push({ startShot: classes[runStart].shotId, endShot: classes[i - 1].shotId, class: classes[runStart].class, length });
      }
      runStart = i;
    }
  }

  return {
    name: "CameraLanguageEngine",
    sequence: classes,
    badRuns,
    score: Math.max(0, 100 - badRuns.length * 15),
    passed: badRuns.length === 0,
    rule: "Prefer wide → medium → close → macro → release wide. Never macro→macro→macro→macro."
  };
}
