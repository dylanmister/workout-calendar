# The White Lotus Training Arc: *Mastering All Elements*

A 164-day beach-volleyball strength, power and mobility calendar (Mon Oct 19, 2026 to Wed Mar 31, 2027), themed on the four elements. It's plain HTML, CSS and JavaScript with no backend. Progress, set logs, notes and schedule shifts are saved in your browser (localStorage).

| Element | Day | Focus |
|---|---|---|
| Earth | 1 | Legs |
| Water | 2 | Back & Biceps |
| Fire | 3 | Chest, Triceps & Shoulders |
| Air | 4 | Rest + Mobility |

Phases: **Foundation** (Oct–Nov), **Strength** (Dec–Jan), **Power** (Feb), **Peak** (Mar).

## Run it locally
Browsers block data files on `file://`, so serve the folder:
```
python -m http.server 8000
```
Then open http://localhost:8000.

- **Time travel:** add `?today=2026-12-15` to the URL to preview any date (handy for testing).
- **Phone preview on desktop:** open http://localhost:8000/tools/phone-preview.html. It shows a 390px-wide frame.

## Deploy
The folder is deployable as-is. All paths are relative and routing uses `#/…`.
- **GitHub Pages:** push the folder to a repo, then go to Settings → Pages → Deploy from branch (root).
- **Netlify:** drag the folder onto app.netlify.com/drop.

After editing `app.js` or `styles.css`, bump the `?v=` numbers in `index.html` so phones load the new files.

## Features
- **Today view:** opens on the current day's workout.
- **Calendar:** color-coded by element, with Gym / Sand / G+S labels. Tap any day to open it.
- **Checklist:** Pai Sho tile checkboxes. Tap a photo to enlarge it (start and finish frames).
- **Set logging:** weight × reps for each set, with last time's numbers shown to beat.
- **Celebration:** shown when every item on a day is checked.
- **Progress:** streaks, the Avatar State meter, per-element bars and best lifts.
- **Push schedule back a day:** shifts that workout and everything after it by one day and extends the end date. It has undo, and the shift count is shown.
- **Backups:** More → Export / Import (JSON) to back up or move devices.

## Project layout
```
index.html  styles.css  app.js  icon.svg  manifest.webmanifest
data/schedule.json        164 days of workouts (exercise references by id)
data/exercises.json       exercise library: name, cues, image paths
data/content.json         original quote for each day, humor strings
data/image-credits.json   source, author and license for every image
images/                   WebP photos (≤800px) + thumbs/ + placeholders/ (SVG)
tools/                    generators and checks (not needed to run the site)
```

## Regenerating data (optional, Python 3 + Pillow + requests)
```
python tools/build_data.py                     # schedule.json + exercises.json
python tools/build_images.py                   # downloads/converts images, writes credits
python tools/build_content.py                  # content.json: daily quotes + humor strings
python tools/verify.py                         # checks 164 days, order, labels, ids, images
```

## Credits
- **Exercise photos:** [free-exercise-db](https://github.com/yuhonas/free-exercise-db) (Unlicense / public domain), plus 19 photos from Pexels, Unsplash and Wikimedia Commons, credited in-app.
- **Placeholders:** 14 exercises with no correct openly licensed photo use original illustrations.
- **Quotes:** original lines in the spirit of *Avatar: The Last Airbender*. This is a personal fan project, not affiliated with Nickelodeon.
