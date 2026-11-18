# Retro beach-volleyball redesign

The site borrows the visual language of a retro beach-volleyball poster: deep ink, sun-bleached sand and cream, and neon sun, coral, hot pink and cyan, with sticker outlines and hard shadows. Only the color, type and texture system changed. The calendar keeps its own layout, structure and identity: the element days, banners, pull quotes, checklists, Polaroid progress photos, starburst badges and ticket-stub phases are all still here. Routes, wording, data, progress storage and sync are unchanged, and every original string still renders.

## Visual system

- **Color:** tokens live at the top of `styles.css`: ink `#1b1340`, sand `#fbf0d9`, paper `#fffaf0`, and the four accents sun `#ffd23f`, coral `#ff7a29`, hot pink `#ff3d8b` and cyan `#00b8c9`. Each element takes one accent (Earth sun, Water cyan, Fire coral, Air pink) and has a fill, a text-safe ink, a tint, and ink text on the fill. Text and button pairs meet WCAG AA contrast.
- **Type:** Bungee for display and section headings, Shrikhand for titles (day titles, page and month titles, dialogs), Yellowtail for script accents (the tagline, Polaroid captions, quote attributions, the photo viewer), and Rubik for body text, buttons and labels. All come from Google Fonts.
- **Stickers:** 2.5px solid ink borders, hard `5px 5px 0` ink shadows with no blur, and a 16px radius on cards. On dark surfaces the sticker outline turns cream and the shadow turns hot pink.
- **Background:** sand, with the supplied cloudscape shader drifting in sand tones, a sun glow top-right, a pink bleed on the left, and a film-grain noise layer. All of it sits behind the content, so cards, photos and the camera stay crisp.
- **Header:** deep ink with a 5px stripe in the four accents underneath. On screens 900px and narrower, the navigation folds into a **Menu** button that opens a slide-in drawer. The drawer is a labelled dialog: focus moves into it and stays there, Escape or a tap outside closes it, and choosing a page closes it. It replaces the old bottom tab bar.
- **Day banners:** four original striped-sun illustrations in `images/retro/` (mountains, waves, flames, clouds) with ink outlines, about 2 to 4 KB each. The decorative "Day N" starburst is hidden from screen readers because the date line already says it.

## Progress photos

- Photos always keep their own shape. Frames take each photo's width and height (stored with the photo), images use `object-fit: contain`, and no image container is forced to a fixed height, so nothing is cropped or stretched. That covers the day card, gallery tiles, the progress strip, the photo calendar, side-by-side and slider compare, and the viewer.
- The camera opens on the rear (environment-facing) camera every time. The ↩ **Flip** button switches between front and rear before the photo is taken. It appears whenever the device has more than one camera, and falls back to choosing the other camera where a browser can't tell front from back. Only the front camera's preview is mirrored, and photos are saved as previewed.

## Files

- `styles.css`: the whole visual system, including the drawer, photo section, gallery, viewer and camera.
- `design.js`: masthead layout, reveal on scroll, and dialog focus handling (now also used by the menu drawer).
- `cloudscape.js`: only its colors changed.
- `images/atlas/`: an older design's landscapes, no longer referenced.

## Verification

Checked in Chromium at 320, 390, 820, 1024 and 1440 px. No route scrolls sideways, with or without the drawer and dialogs open. Reduced motion is respected and keyboard focus stays inside open dialogs. Every string from `tools/design-baseline/copy.json` still renders under the baseline's conditions. The functional and progress photo tests are described in CLOUD-SETUP.md.
