"""
Scans assets/motion, assets/design and assets/brand and writes assets/manifest.js.

Run this from the portfolio-vercel folder after adding, removing or renaming files:
    python make_manifest.py

Files are shown in name order, so prefix them with numbers (01-, 02-, ...).
Portrait or landscape is detected from each file's size automatically.
Images need Pillow once:  pip install pillow
"""
import json
import os
import re
import struct
import sys
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
SECTIONS = ["motion", "design", "brand"]
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXT = {".mp4", ".webm", ".mov"}


def natural_key(name):
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", name)]


def image_size(path):
    from PIL import Image  # pip install pillow
    with Image.open(path) as im:
        return im.size


def _boxes(f, start, end):
    """Yield (type, payload_start, box_end) for the MP4 boxes between start and end."""
    pos = start
    while pos < end:
        f.seek(pos)
        hdr = f.read(8)
        if len(hdr) < 8:
            return
        size, typ = struct.unpack(">I4s", hdr)
        header_len = 8
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            header_len = 16
        elif size == 0:
            size = end - pos
        if size < header_len:
            return
        yield typ.decode("latin1"), pos + header_len, pos + size
        pos += size


def video_size(path):
    """Read the displayed width and height from the first video track's tkhd box."""
    with open(path, "rb") as f:
        total = os.path.getsize(path)
        for name, s, e in _boxes(f, 0, total):
            if name != "moov":
                continue
            for tname, ts, te in _boxes(f, s, e):
                if tname != "trak":
                    continue
                for kname, ks, _ in _boxes(f, ts, te):
                    if kname != "tkhd":
                        continue
                    f.seek(ks)
                    version = f.read(1)[0]
                    matrix = ks + (40 if version == 0 else 52)
                    f.seek(matrix)
                    a, b = struct.unpack(">ii", f.read(8))
                    f.seek(matrix + 36)
                    w, h = struct.unpack(">II", f.read(8))
                    w, h = w / 65536, h / 65536
                    if w == 0 or h == 0:
                        continue  # audio track
                    if abs(a / 65536) < 0.5 and abs(b / 65536) > 0.5:
                        w, h = h, w  # rotated 90 or 270 degrees (phone portrait video)
                    return int(w), int(h)
    raise ValueError("no video track found")


def main():
    if not os.path.isdir(ASSETS):
        sys.exit("No assets folder found next to this script.")

    manifest = {}
    for sec in SECTIONS:
        folder = os.path.join(ASSETS, sec)
        items = []
        print(f"[{sec}]")
        if os.path.isdir(folder):
            for name in sorted(os.listdir(folder), key=natural_key):
                path = os.path.join(folder, name)
                ext = os.path.splitext(name)[1].lower()
                if not os.path.isfile(path) or ext not in IMAGE_EXT | VIDEO_EXT:
                    continue
                try:
                    if ext in IMAGE_EXT:
                        w, h = image_size(path)
                        kind = "image"
                    else:
                        w, h = video_size(path)
                        kind = "video"
                except Exception as err:
                    print(f"  skipped {name}: {err}")
                    continue
                if ext == ".mov":
                    print(f"  note: {name} may not play in Chrome; MP4 is safer")
                items.append({"src": f"assets/{sec}/{quote(name)}", "type": kind, "w": w, "h": h})
                print(f"  {name}  {w}x{h}")
        else:
            print("  folder missing (create it and move files in)")
        manifest[sec] = items

    out = os.path.join(ASSETS, "manifest.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("window.PORTFOLIO_MANIFEST = " + json.dumps(manifest, indent=1, ensure_ascii=False) + ";\n")
    total = sum(len(v) for v in manifest.values())
    print(f"\nWrote {out} with {total} files.")


if __name__ == "__main__":
    main()
