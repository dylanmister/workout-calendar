"""Generates the test photos used by tools/photo-qa/e2e.cjs (needs Pillow): portrait and landscape JPEGs, a sideways
JPEG with EXIF orientation 6, a 12 MP phone-size photo, a PNG with transparency, and a fake .jpg that is not an image."""
import sys, os
from PIL import Image, ImageDraw, ImageFont

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.cache', 'photo-qa', 'img')
os.makedirs(out, exist_ok=True)

def scene(w, h, label, hue):
    im = Image.new("RGB", (w, h), (hue, 120, 200 - hue // 2))
    d = ImageDraw.Draw(im)
    for i in range(0, h, max(8, h // 40)):
        d.rectangle([0, i, w, i + h // 80], fill=((hue + i) % 255, 150, 110))
    # a simple "person" silhouette so orientation mistakes are obvious (head at the TOP)
    cx = w // 2
    d.ellipse([cx - w // 10, h // 10, cx + w // 10, h // 10 + w // 5], fill=(60, 40, 30))
    d.rectangle([cx - w // 7, h // 10 + w // 5, cx + w // 7, int(h * .75)], fill=(60, 40, 30))
    try:
        f = ImageFont.truetype("arialbd.ttf", max(24, w // 9))
    except Exception:
        f = ImageFont.load_default()
    d.text((w // 20, int(h * .8)), label, fill=(255, 255, 240), font=f)
    d.text((w // 20, h // 40), "TOP", fill=(255, 255, 0), font=f)
    return im

scene(1200, 1500, "PORTRAIT", 40).save(f"{out}/portrait.jpg", quality=90)
scene(1600, 1000, "LANDSCAPE", 160).save(f"{out}/landscape.jpg", quality=90)
# Stored sideways with EXIF orientation 6 (rotate 90 CW to display): must display upright ("TOP" at top).
up = scene(900, 1200, "EXIF-6", 90)
sideways = up.transpose(Image.Transpose.ROTATE_90)  # stored landscape 1200x900
exif = Image.Exif(); exif[0x0112] = 6
sideways.save(f"{out}/exif6.jpg", quality=90, exif=exif.tobytes())
# Large phone-sized image
scene(4032, 3024, "BIG 12MP", 200).save(f"{out}/big.jpg", quality=92)
# PNG with transparency
p = scene(800, 1000, "PNG", 120).convert("RGBA")
px = p.load()
for y in range(0, 1000, 2):
    for x in range(0, 200):
        px[x, y] = (0, 0, 0, 0)
p.save(f"{out}/alpha.png")
with open(f"{out}/not-an-image.jpg", "wb") as fh:
    fh.write(b"this is not an image" * 50)
print("ok", sorted(os.listdir(out)))
