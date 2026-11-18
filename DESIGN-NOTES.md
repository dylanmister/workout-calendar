# Retro training journal redesign

The site reads like a 1970s fitness magazine crossed with an athletic training journal: faded cream paper, espresso-brown ink, burnt orange, mustard, forest green and muted brown, with sunset stripes, starbursts, rubber stamps and Polaroids. It is a visual redesign of the same application: routes, wording, data, progress storage and sync are unchanged, and every original string still renders.

## Visual system

- **Type:** Fraunces (a soft, Cooper-style display serif) for headings, Oswald condensed caps for labels, buttons and navigation, Work Sans for body text, and Caveat handwriting for Polaroid captions and session notes. All come from Google Fonts and only download when used.
- **Color:** tokens live at the top of `styles.css`. Each element has a fill, a text-safe ink, a tint and an "on fill" text color (Air days use ink on mustard). Text and button pairs were checked for WCAG AA contrast.
- **Paper:** the supplied cloudscape shader now drifts in cream and beige, so it reads as mottled aged paper. A light grain and halftone sit on top. Dialogs and the camera sit above the grain so photos stay clean.
- **Print details:** hand-cut card corners, hard offset shadows, sunset stripe bands, starburst badges, ticket-stub phases, dotted record-book leaders, ruled index-card set logs, a ruled journal page for notes, and rubber-stamp checkmarks.
- **Day banners:** four original striped-sunset illustrations in `images/retro/` (mountains, waves, flames, clouds), each about 2 to 3 KB. The decorative "Day N" starburst on the banner is hidden from screen readers because the date line already says it.

## Files

- `styles.css`: the whole visual system, including the progress photo section, gallery, viewer and camera.
- `design.js`: unchanged behavior (masthead layout, reveal on scroll, dialog focus handling); the photo section and gallery months are added to the reveal list.
- `cloudscape.js`: only its three colors and speed changed.
- `images/atlas/`: the previous design's landscapes, no longer referenced.

## Verification

Checked in Chromium at 320, 390, 768, 820, 1024 and 1440 px: no horizontal scrolling on any route (including the gallery and open dialogs), reduced motion respected, keyboard focus contained in dialogs, and every string from `tools/design-baseline/copy.json` still rendered under the baseline's conditions. Functional checks (checklists, completion, logs, notes, supplements, push/undo, calendar, units, backup export/import, cloud sync) and the progress photo tests are described in CLOUD-SETUP.md.
