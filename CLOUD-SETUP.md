# Hosted sign-in and shared progress

Production: **https://white-lotus-training-arc.vercel.app**

Sign in with the password supplied for this project. Every device uses the same private training account. Checklists, completed days, set logs, notes, weight units, and schedule shifts are stored in Convex and cached locally. Existing progress in the browser is merged into the cloud on its first authenticated visit. To migrate progress from a different site address, export it there, then import it on the production site after signing in.

The supplied cloudscape shader runs across every route, including sign-in. It uses a capped drawing resolution and frame rate, pauses in hidden tabs, and renders a still frame when reduced motion is requested. Browsers without WebGL retain the CSS background.

## Architecture

- `account.js`: sign-in interface and initialization gate.
- `api/session.js`: server-side password verification, persistent login-attempt limiting, and signed HTTP-only session cookies.
- `api/progress.js`: authenticated proxy for the shared account's Convex progress.
- `server/auth.cjs`: password hashing/verification, session signatures, origin checks, and Convex requests.
- `convex/progress.js`: revision-based saves to avoid blindly overwriting a newer cloud copy.
- `convex/login.js`: login attempt limits persisted in the database.
- `cloudscape.js`: supplied GLSL shader adapted to plain JavaScript without React.

The password verifier, session signing secret, shared account identifier, and backend access key live in Vercel environment variables. Convex also requires the backend access key. These values are never returned to browser JavaScript. The local deployment helper retains secrets under ignored `tools/.cache/`; the entire tools folder is excluded from Vercel uploads.

## Deploy updates

```powershell
node node_modules/convex/bin/main.js deploy --yes
vercel deploy --prod --yes
```

Both CLIs must be signed in to the existing linked accounts. Environment variables are already configured. Do not regenerate or rotate the shared account identifier during routine deployment; doing so would select a different progress record.

## Verification

`tools/cloud-server.cjs` runs the real Vercel handlers locally against a separate Convex development deployment and a random test account. `tools/cloud-test.cjs` checks wrong-password rejection, unauthorized data access, two independent browser profiles sharing checks/logs/notes/shifts, unchecking propagation, session persistence, logout, and shader initialization.

`tools/live-check.cjs` checks the production site with two independent profiles and round-trips its existing state without changing its content. It checks secure cookies, the four main routes, mobile overflow, cloudscape presence, and sign-out.

Browser tests require Playwright/Chromium. Development harness:

```powershell
node tools/cloud-server.cjs
# In another terminal:
node tools/cloud-test.cjs
```

The original design-audit integrity test intentionally reflects the pre-authentication application. Its app.js hash will differ now because the new authentication and synchronization features change application behavior.
