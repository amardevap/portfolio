"""
Shrinks the images in assets/motion, assets/design and assets/brand so the site loads fast.

- Images are resized so their longest side is at most 2000 px and saved as JPG.
- PNGs with transparency get a white background (no black edges).
- The original files are moved to ..\\portfolio-originals, outside the project,
  so nothing is lost.
- Videos are not changed. Any file over 100 MB is listed, because GitHub rejects it.

Run from the portfolio-vercel folder, then run make_manifest.py again:
    py shrink_images.py
Needs Pillow:  py -m pip install pillow
"""
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
BACKUP = os.path.join(ROOT, "..", "portfolio-originals")
SECTIONS = ["motion", "design", "brand"]
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXT = {".mp4", ".webm", ".mov"}
MAX_SIDE = 2000
QUALITY = 85
GITHUB_LIMIT = 100 * 1024 * 1024


def flatten(im):
    """Return an RGB image, with transparent areas painted white."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def free_path(path):
    """Return path, or path with -1, -2... added, so nothing is overwritten."""
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(path)
    n = 1
    while os.path.exists(f"{base}-{n}{ext}"):
        n += 1
    return f"{base}-{n}{ext}"


def shrink(path, sec, name):
    stem, ext = os.path.splitext(name)
    with Image.open(path) as im:
        w, h = im.size
        if max(w, h) <= MAX_SIDE and ext.lower() in (".jpg", ".jpeg"):
            print(f"  kept   {name}  {w}x{h} (already small)")
            return
        out = flatten(im)
    out.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)

    tmp = os.path.join(ASSETS, sec, stem + ".__tmp__.jpg")
    out.save(tmp, "JPEG", quality=QUALITY, optimize=True, progressive=True)

    backup_dir = os.path.join(BACKUP, sec)
    os.makedirs(backup_dir, exist_ok=True)
    shutil.move(path, free_path(os.path.join(backup_dir, name)))

    final = os.path.join(ASSETS, sec, stem + ".jpg")
    if os.path.exists(final) and os.path.abspath(final) != os.path.abspath(path):
        final = free_path(final)
    os.replace(tmp, final)
    print(f"  shrunk {name} -> {os.path.basename(final)}  {w}x{h} -> {out.size[0]}x{out.size[1]}")


def main():
    if not os.path.isdir(ASSETS):
        sys.exit("No assets folder found next to this script.")

    big = []
    for sec in SECTIONS:
        folder = os.path.join(ASSETS, sec)
        if not os.path.isdir(folder):
            continue
        print(f"[{sec}]")
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            ext = os.path.splitext(name)[1].lower()
            if not os.path.isfile(path):
                continue
            if ext in IMAGE_EXT:
                try:
                    shrink(path, sec, name)
                except Exception as err:
                    print(f"  skipped {name}: {err}")
            elif ext in VIDEO_EXT and os.path.getsize(path) > GITHUB_LIMIT:
                big.append((name, os.path.getsize(path)))

    print()
    if big:
        print("These videos are over 100 MB. GitHub will reject them. Compress them first:")
        for name, size in big:
            print(f"  {name}  {size / 1024 / 1024:.0f} MB")
    print("Done. Now run:  py make_manifest.py")


if __name__ == "__main__":
    main()
