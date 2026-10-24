# Illustrated training atlas redesign

The original application, data, routes, wording, progress storage, and optional Convex sync implementation are preserved. The visual redesign uses warm ivory, forest ink, brass details, element-specific accents, editorial serif typography, larger exercise photographs, and four original SVG landscapes.

## Implementation

- `styles.css`: replaces the visual system, including all routes, dialogs, charts, logging forms, and responsive layouts. No layered legacy stylesheet or UI framework.
- `design.js`: moves the existing daily banner and controls into a full-width masthead without changing their text or reading order. IntersectionObserver reveals content; keyboard focus stays within dialogs and returns to its trigger. Motion respects the device's reduced-motion setting.
- `index.html`: updates the stylesheet cache version and loads the enhancement script. Existing text is untouched.
- `images/atlas/`: four original code-drawn SVG landscapes. All four together are approximately 10 KB. They are decorative CSS backgrounds and do not replace exercise images. Regenerate with `python tools/design-art.py`.

## Run

```powershell
python -m http.server 8010 --bind 127.0.0.1
```

Open `http://127.0.0.1:8010`. Existing deployment configuration and routes remain unchanged. No new runtime packages are needed.

## Verification

```powershell
node --check app.js
node --check design.js
python -X utf8 tools/verify.py
node tools/design-qa/verify.cjs
```

The browser test requires Playwright and Chromium. It resolves Playwright from this folder or the existing neighboring `codex training calendar` development installation. To use this test elsewhere, install Playwright locally as a development tool and run `npx playwright install chromium`.

The retained baseline records the rendered wording on eight original routes and hashes the original app and all JSON data files. Tests compare the redesigned pages to that baseline, exercise logging and notes persistence, image enlargement and frames, calendar navigation, schedule shift and undo, completion, units, backup export/import, keyboard containment, and reduced motion. Layout checks cover 320, 390, 768, and 1440 pixels. Before/after screenshots are saved under `tools/design-qa/`.

Cloud sync is left unchanged and disabled in isolated browser tests, so those tests do not modify a cloud copy. A running Convex backend is required to verify actual cross-device synchronization. No deployment was performed.
