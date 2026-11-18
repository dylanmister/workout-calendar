# Hosted sign-in and shared progress

Production: **https://white-lotus-training-arc.vercel.app**

Sign in with the password supplied for this project. Every device uses the same private training account. Checklists, completed days, set logs, notes, supplements, weight units, and schedule shifts are stored in Convex and cached locally. Daily progress photos are stored in Convex file storage (never in the browser) and are only reachable while signed in. Existing progress in the browser is merged into the cloud on its first authenticated visit. To migrate progress from a different site address, export it there, then import it on the production site after signing in.

The supplied cloudscape shader runs across every route, including sign-in, recolored to sun-bleached sand for the retro beach design. It uses a capped drawing resolution and frame rate, pauses in hidden tabs, and renders a still frame when reduced motion is requested. Browsers without WebGL retain the CSS background.

## Architecture

- `account.js`: sign-in interface and initialization gate.
- `api/session.js`: server-side password verification, persistent login-attempt limiting, and signed HTTP-only session cookies.
- `api/progress.js`: authenticated proxy for the shared account's Convex progress.
- `server/auth.cjs`: password hashing/verification, session signatures, origin checks, and Convex requests.
- `convex/progress.js`: revision-based saves to avoid blindly overwriting a newer cloud copy.
- `convex/login.js`: login attempt limits persisted in the database.
- `api/photos.js`: signed-in list, save (replacing that day's photo), and delete for progress photos.
- `api/photo.js`: streams one photo (full size or thumbnail) to the signed-in browser, so storage URLs never leave the server. Versioned photo URLs may be cached privately by the browser; `vercel.json` therefore limits its `no-store` rule to the JSON endpoints.
- `server/photos.cjs`: date and JPEG checks shared by the photo endpoints.
- `convex/photos.js` and the `photos` table: one row per date holding a full-size JPEG (at most 1600 px) and a thumbnail (640 px). Replacing or removing a photo deletes its old files.
- `cloudscape.js`: supplied GLSL shader adapted to plain JavaScript without React.

The password verifier, session signing secret, shared account identifier, and backend access key live in Vercel environment variables. Convex also requires the backend access key. These values are never returned to browser JavaScript. The local deployment helper retains secrets under ignored `tools/.cache/`; the entire tools folder is excluded from Vercel uploads.

## Deploy updates

Deploy the Convex functions first whenever `convex/` changes (the photo feature added the `photos` table and functions), then ship the site:

```powershell
node node_modules/convex/bin/main.js deploy --yes
git push origin main
```

The Vercel project is connected to GitHub, so pushing `main` deploys production by itself; running `vercel deploy --prod` as well would create a second, identical deployment. The Convex CLI must be signed in to the existing linked account. Environment variables are already configured. Do not regenerate or rotate the shared account identifier during routine deployment; doing so would select a different progress record.

## Verification

`tools/cloud-server.cjs` runs the real Vercel handlers locally against a separate Convex development deployment and a random test account. `tools/cloud-test.cjs` checks wrong-password rejection, unauthorized data access, two independent browser profiles sharing checks/logs/notes/shifts, unchecking propagation, session persistence, logout, and shader initialization.

`tools/live-check.cjs` checks the production site with two independent profiles and round-trips its existing state without changing its content. It checks secure cookies, the four main routes, mobile overflow, cloudscape presence, and sign-out.

Browser tests require Playwright/Chromium. Development harness:

```powershell
node tools/cloud-server.cjs
# In another terminal:
node tools/cloud-test.cjs
```

Progress photos and the retro redesign were verified with `tools/photo-qa/` (see the comment at the top of each file). It runs the real API handlers against the Convex development deployment with a throwaway password, so it never needs or touches the real password or production data:

```powershell
python tools/photo-qa/make-images.py    # test photos (needs Pillow)
node tools/photo-qa/harness.cjs         # in another terminal
node tools/photo-qa/api.cjs             # sign-in and same-origin rules, validation, caching, replace, delete, failed-save cleanup
node tools/photo-qa/e2e.cjs             # upload, camera, timer, replace, gallery, viewer, compare, remove, denied camera
node tools/photo-qa/regression.cjs      # checklists, logs, notes, supplements, shifts, backups, sync, layouts
node tools/photo-qa/ui-check.cjs        # mobile menu drawer, rear camera by default + flip, photos keep their own shape
```

`node tools/photo-qa/copy-check.cjs` confirms every original string still renders; it needs the harness in signed-out mode on port 8032 (`QA_STATIC=1`, `QA_PORT=8032`). Each harness run uses a new random test account in the development database.

The camera tests use Chromium's built-in fake camera; a real phone's camera should still be tried once after each deployment.

The original design-audit integrity test intentionally reflects the pre-authentication application. Its app.js hash will differ now because the new authentication and synchronization features change application behavior.
