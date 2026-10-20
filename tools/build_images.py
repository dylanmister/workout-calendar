"""Builds every exercise image referenced by data/exercises.json.

  * free-exercise-db photos (public domain): start + finish frames -> images/<id>.webp, images/<id>-2.webp
  * external photos listed in tools/image_sources.json (Wikimedia Commons / Pexels / Unsplash) -> images/<id>.webp
  * everything else -> an illustrated SVG placeholder in the element's color -> images/placeholders/<id>.svg
  * thumbnails (360 x 240) for every photo -> images/thumbs/<id>.webp
  * data/image-credits.json records source URL, author and license for every image

Run:  python tools/build_images.py [--cache DIR] [--only id,id] [--force]
Downloads are cached in DIR (default tools/.cache) so re-runs are cheap.
"""
import argparse
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from html import escape

import requests
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from library import EX  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
FEDB_RAW = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"
FEDB_PAGE = "https://github.com/yuhonas/free-exercise-db/tree/main/exercises/"
UA = "WhiteLotusTrainingArc/1.0 (personal workout calendar; image build script)"
FULL_W, THUMB = 800, (360, 240)

ELEMENT_COLORS = {  # bg top, bg bottom, accent, ink
    "earth": ("#eef0dc", "#d9d2b1", "#4f7a33", "#3d2f1f"),
    "water": ("#e6f1f7", "#c6dceb", "#2a6b9c", "#1f3448"),
    "fire": ("#fbeadb", "#f2c9a8", "#c2410c", "#4a2412"),
    "air": ("#fdf7dd", "#e2eff5", "#b88a12", "#3b3a2a"),
}


def fetch(url, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    ext = os.path.splitext(url.split("?")[0])[1][:5] or ".img"
    name = hashlib.md5(url.encode("utf-8")).hexdigest()[:16] + ext  # short: Windows paths max out at 260 chars
    path = os.path.join(cache_dir, name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    for attempt in range(4):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
            r.raise_for_status()
            with open(path, "wb") as f:
                f.write(r.content)
            return path
        except Exception as e:  # noqa: BLE001
            if attempt == 3:
                raise RuntimeError(f"download failed {url}: {e}")
            time.sleep(2 * (attempt + 1))


def open_rgb(path):
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGB")


def save_full(im, out):
    if im.width > FULL_W:
        im = im.resize((FULL_W, round(im.height * FULL_W / im.width)), Image.LANCZOS)
    im.save(out, "WEBP", quality=72, method=6)


def save_thumb(im, out, focus=(0.5, 0.5), mode="cover"):
    if mode == "contain":  # tall photos: keep the whole movement visible on a parchment background
        th = Image.new("RGB", THUMB, (239, 227, 196))
        fit = ImageOps.contain(im, THUMB, Image.LANCZOS)
        th.paste(fit, ((THUMB[0] - fit.width) // 2, (THUMB[1] - fit.height) // 2))
    else:
        th = ImageOps.fit(im, THUMB, Image.LANCZOS, centering=focus)
    th.save(out, "WEBP", quality=68, method=6)


# ---------------------------------------------------------------- placeholder pictograms (200x200 box)
def _p(pts):
    return " ".join(f"{x},{y}" for x, y in pts)


POSES = {
    "stand": dict(head=(100, 38), lines=[[(100, 50), (100, 108)], [(100, 64), (78, 46), (74, 22)], [(100, 64), (122, 46), (126, 22)],
                                         [(100, 108), (90, 136), (88, 168)], [(100, 108), (110, 136), (112, 168)]]),
    "jump": dict(head=(100, 30), lines=[[(100, 42), (100, 96)], [(100, 56), (82, 34), (76, 12)], [(100, 56), (118, 34), (124, 12)],
                                        [(100, 96), (84, 120), (94, 146)], [(100, 96), (116, 120), (106, 146)]],
                 extra=[[(70, 168), (130, 168)], [(80, 180), (120, 180)]]),
    "sprint": dict(head=(122, 38), lines=[[(116, 50), (96, 102)], [(112, 62), (134, 80), (146, 64)], [(112, 62), (88, 76), (80, 98)],
                                          [(96, 102), (128, 120), (124, 154)], [(96, 102), (74, 134), (50, 146)]],
                   extra=[[(30, 70), (60, 70)], [(22, 90), (52, 90)], [(30, 110), (56, 110)]]),
    "shuffle": dict(head=(100, 50), lines=[[(100, 62), (96, 108)], [(98, 76), (76, 98)], [(98, 76), (122, 98)],
                                           [(96, 108), (70, 136), (64, 168)], [(96, 108), (124, 136), (132, 168)]],
                    extra=[[(20, 186), (60, 186)], [(20, 186), (30, 180)], [(20, 186), (30, 192)],
                           [(140, 186), (180, 186)], [(180, 186), (170, 180)], [(180, 186), (170, 192)]]),
    "sideplank": dict(head=(52, 86), lines=[[(64, 98), (168, 120)], [(70, 100), (66, 146), (92, 146)], [(96, 104), (110, 64)]],
                      rects=[(150, 120, 44, 10)], extra=[[(154, 130), (154, 150)], [(190, 130), (190, 150)], [(40, 150), (150, 150)]]),
    "squat": dict(head=(110, 46), lines=[[(106, 58), (86, 112)], [(102, 70), (138, 82)], [(86, 112), (126, 114), (120, 156)],
                                         [(86, 112), (120, 120), (112, 156)]], extra=[[(70, 160), (150, 160)]]),
    "lunge": dict(head=(100, 40), lines=[[(100, 52), (100, 108)], [(100, 62), (92, 20)], [(100, 62), (108, 20)],
                                         [(100, 108), (132, 122), (132, 160)], [(100, 108), (80, 152), (54, 158)]],
                  extra=[[(40, 162), (160, 162)]]),
    "stretchfloor": dict(head=(150, 104), lines=[[(80, 150), (172, 150)], [(80, 150), (140, 114)], [(132, 120), (166, 142)]],
                         extra=[[(40, 156), (186, 156)]]),
    "yoga": dict(head=(70, 132), lines=[[(48, 160), (112, 70)], [(112, 70), (166, 160)]], extra=[[(30, 164), (180, 164)]]),
    "swim": dict(head=(58, 94), lines=[[(70, 100), (160, 106)], [(80, 98), (60, 70), (38, 80)], [(86, 102), (112, 120)],
                                       [(160, 106), (186, 96)], [(160, 106), (186, 116)]], waves=True),
    "walk": dict(head=(100, 38), lines=[[(100, 50), (100, 104)], [(100, 64), (86, 94)], [(100, 64), (116, 92)],
                                        [(100, 104), (84, 160)], [(100, 104), (118, 158)]],
                 dots=[(40, 172), (62, 178), (138, 172), (160, 178)]),
    "breathe": dict(head=(100, 58), lines=[[(100, 70), (100, 124)], [(100, 84), (76, 114), (72, 128)], [(100, 84), (124, 114), (128, 128)],
                                           [(100, 128), (64, 140), (96, 148)], [(100, 128), (136, 140), (104, 148)]], swirls=True),
    "crawl": dict(head=(52, 92), lines=[[(70, 104), (140, 108)], [(70, 104), (70, 160)], [(140, 108), (142, 146), (176, 152)],
                                        [(140, 108), (128, 146)]], extra=[[(40, 164), (186, 164)]]),
    # exercise-specific pictograms for the placeholders that need them
    "ninety": dict(head=(100, 74), lines=[[(100, 86), (100, 140)], [(100, 100), (72, 130)], [(100, 100), (130, 122)],
                                          [(100, 140), (62, 150), (112, 166)], [(100, 140), (138, 150), (164, 132)]],
                   extra=[[(40, 172), (180, 172)]]),
    "legswing": dict(head=(106, 38), lines=[[(106, 50), (106, 108)], [(106, 64), (78, 80), (54, 82)], [(106, 64), (128, 84)],
                                            [(106, 108), (102, 168)], [(106, 108), (146, 134), (168, 126)]],
                     extra=[[(48, 56), (48, 172)], [(36, 172), (176, 172)]],
                     paths=[("M150 162 Q182 146 176 110", "6 6")]),
    "tibialis": dict(head=(74, 36), lines=[[(76, 48), (82, 112)], [(78, 62), (86, 98)], [(82, 112), (112, 166), (130, 152)],
                                           [(82, 112), (118, 164), (136, 150)]],
                     extra=[[(60, 16), (60, 172)], [(48, 172), (176, 172)]], paths=[("M150 166 Q160 150 150 134", "5 5")]),
    "wallslide": dict(head=(100, 40), lines=[[(100, 52), (100, 110)], [(100, 62), (72, 62), (72, 32)], [(100, 62), (128, 62), (128, 32)],
                                             [(100, 110), (90, 170)], [(100, 110), (110, 170)]],
                      rects=[(56, 12, 88, 160, .14)], extra=[[(72, 22), (72, 10)], [(128, 22), (128, 10)]]),
    "halo": dict(head=(100, 54), lines=[[(100, 66), (100, 120)], [(100, 78), (78, 60), (92, 34)], [(100, 78), (122, 60), (108, 34)],
                                        [(100, 120), (90, 172)], [(100, 120), (110, 172)]],
                 circles=[(100, 26, 10)], paths=[("M62 52 A40 15 0 1 0 138 52", "6 6")]),
    "openbook": dict(head=(52, 136), lines=[[(64, 142), (126, 146)], [(126, 146), (150, 126), (172, 150)], [(70, 144), (104, 152)],
                                            [(70, 140), (64, 96)]],
                     extra=[[(30, 162), (190, 162)]], paths=[("M104 132 Q100 92 70 88", "6 6")]),
    "sleeper": dict(head=(52, 132), lines=[[(64, 138), (132, 144)], [(132, 144), (160, 152), (186, 156)], [(68, 140), (98, 128), (98, 98)],
                                           [(72, 134), (102, 106)]],
                    extra=[[(30, 162), (196, 162)]], paths=[("M116 92 Q124 110 112 124", "5 5")]),
    "spanish": dict(head=(100, 48), lines=[[(96, 60), (80, 116)], [(96, 72), (136, 84)], [(80, 116), (116, 118), (114, 162)],
                                           [(80, 116), (112, 124), (108, 162)]],
                    extra=[[(40, 60), (40, 172)], [(30, 172), (170, 172)]], paths=[("M40 120 L114 118", "7 5")]),
    "trapjump": dict(head=(100, 28), lines=[[(100, 40), (100, 92)], [(100, 54), (84, 88)], [(100, 54), (116, 88)],
                                            [(100, 92), (86, 118), (94, 144)], [(100, 92), (114, 118), (106, 144)]],
                     polys=[[(70, 90), (80, 80), (120, 80), (130, 90), (120, 100), (80, 100)]],
                     extra=[[(70, 168), (130, 168)], [(80, 180), (120, 180)]]),
    "pogo": dict(head=(100, 30), lines=[[(100, 42), (100, 100)], [(100, 56), (86, 82), (92, 98)], [(100, 56), (114, 82), (108, 98)],
                                        [(100, 100), (96, 150)], [(100, 100), (104, 150)]],
                 extra=[[(70, 172), (130, 172)], [(92, 158), (92, 164)], [(108, 158), (108, 164)]]),
}
PICT_OVERRIDE = {"90-90-switch": "ninety", "leg-swings": "legswing", "tibialis-raise": "tibialis", "wall-slide": "wallslide",
                 "kb-halo": "halo", "open-book": "openbook", "sleeper-stretch": "sleeper", "spanish-squat": "spanish",
                 "trap-bar-jump": "trapjump", "pogo-hops": "pogo"}


def glyph(element, accent):
    if element == "earth":
        return f'<path d="M20 70 L55 18 L72 40 L88 22 L120 70 Z" fill="{accent}" opacity=".16"/>'
    if element == "water":
        return (f'<path d="M10 50 q20 -24 40 0 t40 0 t40 0" fill="none" stroke="{accent}" stroke-width="8" opacity=".18" stroke-linecap="round"/>'
                f'<path d="M10 74 q20 -24 40 0 t40 0 t40 0" fill="none" stroke="{accent}" stroke-width="8" opacity=".12" stroke-linecap="round"/>')
    if element == "fire":
        return f'<path d="M60 90 C20 70 40 40 52 20 C58 40 70 42 66 18 C96 40 102 74 60 90 Z" fill="{accent}" opacity=".17"/>'
    return (f'<path d="M64 52 a16 16 0 1 1 16 -16 a28 28 0 1 1 -28 28 a40 40 0 1 1 40 -40" fill="none" stroke="{accent}" '
            f'stroke-width="7" opacity=".18" stroke-linecap="round"/>')


def wrap(name, width=20):
    words, lines, cur = name.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    lines.append(cur)
    return lines[:3]


def placeholder_svg(ex):
    top, bottom, accent, ink = ELEMENT_COLORS[ex["element"]]
    pose = POSES.get(PICT_OVERRIDE.get(ex["id"]) or ex.get("pict") or "stand", POSES["stand"])
    g = []
    for r in pose.get("rects", []):
        if len(r) == 5:  # translucent backdrop (e.g. a wall)
            x, y, w, h, op = r
            g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{accent}" opacity="{op}"/>')
    hx, hy = pose["head"]
    g.append(f'<circle cx="{hx}" cy="{hy}" r="12" fill="{ink}"/>')
    for ln in pose["lines"]:
        g.append(f'<polyline points="{_p(ln)}" fill="none" stroke="{ink}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
    for ln in pose.get("extra", []):
        g.append(f'<polyline points="{_p(ln)}" fill="none" stroke="{accent}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>')
    for r in pose.get("rects", []):
        if len(r) == 4:
            x, y, w, h = r
            g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{accent}" opacity=".85"/>')
    for pts in pose.get("polys", []):
        g.append(f'<polygon points="{_p(pts)}" fill="none" stroke="{accent}" stroke-width="5" stroke-linejoin="round"/>')
    for (cx, cy, rr) in pose.get("circles", []):
        g.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="{accent}"/><path d="M{cx - 6} {cy - rr + 1} Q{cx} {cy - rr - 9} {cx + 6} {cy - rr + 1}" '
                 f'fill="none" stroke="{accent}" stroke-width="3"/>')
    for (d, dash) in pose.get("paths", []):
        g.append(f'<path d="{d}" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round" stroke-dasharray="{dash}"/>')
    for (x, y) in pose.get("dots", []):
        g.append(f'<ellipse cx="{x}" cy="{y}" rx="7" ry="4" fill="{accent}" opacity=".6"/>')
    if pose.get("waves"):
        for i, y in enumerate((126, 144)):
            g.append(f'<path d="M20 {y} q15 -12 30 0 t30 0 t30 0 t30 0 t30 0 t30 0" fill="none" stroke="{accent}" stroke-width="5" '
                     f'opacity="{.8 - i * .3}" stroke-linecap="round"/>')
    if pose.get("swirls"):
        g.append(f'<path d="M66 30 q10 -14 22 -6 q8 8 -2 14" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>')
        g.append(f'<path d="M118 22 q12 -10 22 0 q6 10 -6 14" fill="none" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>')
    lines = wrap(ex["name"])
    fs = 34 if max(len(l) for l in lines) <= 18 else 30
    y0 = 312 - (len(lines) - 1) * (fs * 0.55)
    text = "".join(f'<tspan x="300" y="{y0 + i * fs * 1.15:.0f}">{escape(l)}</tspan>' for i, l in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400" width="600" height="400" role="img" aria-label="{escape(ex["name"])} (illustration)">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient></defs>
<rect width="600" height="400" fill="url(#bg)"/>
<rect x="10" y="10" width="580" height="380" rx="18" fill="none" stroke="{accent}" stroke-width="3" opacity=".55"/>
<rect x="20" y="20" width="560" height="360" rx="12" fill="none" stroke="{ink}" stroke-width="1" opacity=".25"/>
<g transform="translate(430 18) scale(1.1)">{glyph(ex["element"], accent)}</g>
<g transform="translate(172 4) scale(1.28)">{"".join(g)}</g>
<text font-family="Georgia, 'Times New Roman', serif" font-size="{fs}" font-weight="700" fill="{ink}" text-anchor="middle">{text}</text>
<text x="300" y="372" font-family="Georgia, serif" font-size="15" fill="{ink}" opacity=".55" text-anchor="middle" letter-spacing="2">ILLUSTRATED PLACEHOLDER</text>
</svg>
'''


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(ROOT, "tools", ".cache"))
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    exercises = json.load(open(os.path.join(ROOT, "data", "exercises.json"), encoding="utf-8"))["exercises"]
    src_path = os.path.join(ROOT, "tools", "image_sources.json")
    sources = json.load(open(src_path, encoding="utf-8")) if os.path.exists(src_path) else {}
    only = set(filter(None, args.only.split(",")))
    for d in ("", "thumbs", "placeholders"):
        os.makedirs(os.path.join(IMG, d), exist_ok=True)
    credits = []
    jobs = []

    def do_fedb(e):
        lib = EX[e["id"]]
        fid = lib["fedb"]
        out0 = os.path.join(IMG, f"{e['id']}.webp")
        out1 = os.path.join(IMG, f"{e['id']}-2.webp")
        outt = os.path.join(IMG, "thumbs", f"{e['id']}.webp")
        if args.force or not (os.path.exists(out0) and os.path.exists(out1) and os.path.exists(outt)):
            p0 = fetch(FEDB_RAW + f"{fid}/0.jpg", os.path.join(args.cache, "fedb"))
            p1 = fetch(FEDB_RAW + f"{fid}/1.jpg", os.path.join(args.cache, "fedb"))
            im0, im1 = open_rgb(p0), open_rgb(p1)
            save_full(im0, out0)
            save_full(im1, out1)
            save_thumb(im1 if lib.get("frame", 1) == 1 else im0, outt)
        return e["id"]

    def do_external(e):
        s = sources[e["id"]]
        out = os.path.join(IMG, f"{e['id']}.webp")
        outt = os.path.join(IMG, "thumbs", f"{e['id']}.webp")
        if args.force or not (os.path.exists(out) and os.path.exists(outt)):
            p = fetch(s["url"], os.path.join(args.cache, "external"))
            im = open_rgb(p)
            if s.get("crop"):  # [left, top, right, bottom] fractions
                l, t, r, b = s["crop"]
                im = im.crop((round(l * im.width), round(t * im.height), round(r * im.width), round(b * im.height)))
            save_full(im, out)
            save_thumb(im, outt, tuple(s.get("focus", (0.5, 0.5))), s.get("thumb", "cover"))
        return e["id"]

    for e in exercises:
        if only and e["id"] not in only:
            continue
        lib = EX[e["id"]]
        if lib["fedb"]:
            jobs.append(("fedb", e))
            credits.append(dict(id=e["id"], exercise=e["name"], files=[f"images/{e['id']}.webp", f"images/{e['id']}-2.webp",
                                                                          f"images/thumbs/{e['id']}.webp"],
                                source="free-exercise-db", sourceUrl=FEDB_PAGE + lib["fedb"],
                                imageUrls=[FEDB_RAW + f"{lib['fedb']}/0.jpg", FEDB_RAW + f"{lib['fedb']}/1.jpg"],
                                author="free-exercise-db (yuhonas), from wrkout/exercises.json",
                                license="Unlicense (public domain)", licenseUrl="https://unlicense.org/"))
        elif e["id"] in sources:
            s = sources[e["id"]]
            jobs.append(("ext", e))
            credits.append(dict(id=e["id"], exercise=e["name"], files=[f"images/{e['id']}.webp", f"images/thumbs/{e['id']}.webp"],
                                source=s["site"], sourceUrl=s["page"], imageUrls=[s["url"]], author=s.get("author", ""),
                                license=s["license"], licenseUrl=s.get("licenseUrl", ""),
                                **({"modifications": s["modifications"]} if s.get("modifications") else {})))
        else:
            path = os.path.join(IMG, "placeholders", f"{e['id']}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(placeholder_svg(dict(lib, name=e["name"])))
            credits.append(dict(id=e["id"], exercise=e["name"], files=[f"images/placeholders/{e['id']}.svg"],
                                source="Original illustration", sourceUrl="", imageUrls=[], author="The White Lotus Training Arc",
                                license="Created for this project", licenseUrl="",
                                note="No openly licensed photo showing this exact movement was found, so an illustrated placeholder is used."))
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(do_fedb if kind == "fedb" else do_external, e) for kind, e in jobs]
        for fu in futs:
            fu.result()
            done += 1
            if done % 40 == 0:
                print(f"  {done}/{len(jobs)} images ({time.time() - t0:.0f}s)", flush=True)
    if not only:
        credits.sort(key=lambda c: c["exercise"].lower())
        with open(os.path.join(ROOT, "data", "image-credits.json"), "w", encoding="utf-8") as f:
            json.dump(dict(generated=time.strftime("%Y-%m-%d"), images=credits), f, ensure_ascii=False, indent=1)
    n_ph = sum(1 for c in credits if c["source"] == "Original illustration")
    print(f"done: {len(jobs)} photos processed, {n_ph} placeholders, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
