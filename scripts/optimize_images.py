#!/usr/bin/env python3
"""
Create web-optimised, watermarked WebP copies of original artwork.

    python3 scripts/optimize_images.py            # convert new/changed originals
    python3 scripts/optimize_images.py --force    # re-convert everything

Reads every image under original_heavy/ (recursively) and writes
images/<original name>.webp:
  - longest edge resized down to 2400px (never upscaled)
  - watermark drawn on (see WATERMARK SETTINGS below)
  - WebP, quality 80
  - if the result is over ~500 KB, quality is lowered step by step (to 60),
    then the image is shrunk further, until it fits
  - EXIF orientation is applied; the colour (ICC) profile is kept;
    other metadata (camera info, GPS location) is stripped

Outputs are regenerated automatically when the original OR this script is
newer than the output, so after tweaking a setting just re-run it.

Originals are only ever opened for reading - nothing in original_heavy/
is modified, moved or deleted.
"""

# ===================== WATERMARK SETTINGS (tweak these) =====================
WATERMARK_ENABLED = True
WATERMARK_TEXT = "© Kunal Deoskar"
WATERMARK_SIZE = 0.016       # text height as a fraction of the image's longest edge
                             #   (0.016 -> ~38px on a 2400px image)
WATERMARK_OPACITY = 0.40     # 0.0 = invisible, 1.0 = solid white
WATERMARK_POSITION = "bottom-right"  # bottom-right | bottom-left | top-right | top-left | bottom-center
WATERMARK_MARGIN = 0.025     # gap from the edges, as a fraction of the shorter edge
SHADOW_OPACITY = 0.35        # soft dark shadow behind the text (0 to disable)
SHADOW_BLUR = 0.12           # shadow softness, as a fraction of the text size
SHADOW_OFFSET = 0.05         # shadow drop (down/right), as a fraction of the text size
FONT_CANDIDATES = [          # first one that exists is used
    "/System/Library/Fonts/HelveticaNeue.ttc",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
# ===================== OUTPUT SETTINGS ======================================
MAX_EDGE = 2400
QUALITY = 80
MIN_QUALITY = 60
MAX_BYTES = 500 * 1024
# ============================================================================

import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "original_heavy"
OUT_DIR = ROOT / "images"
INPUT_EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp", ".heic"}

Image.MAX_IMAGE_PIXELS = None  # large scans are expected; they're our own files


def load_font(px: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, px)
    return ImageFont.load_default(px)


def add_watermark(im: Image.Image) -> Image.Image:
    w, h = im.size
    font_px = max(10, round(max(w, h) * WATERMARK_SIZE))
    font = load_font(font_px)
    margin = round(min(w, h) * WATERMARK_MARGIN)

    left, top, right, bottom = font.getbbox(WATERMARK_TEXT)
    tw, th = right - left, bottom - top
    x = {"left": margin, "right": w - margin - tw, "center": (w - tw) // 2}[WATERMARK_POSITION.split("-")[1]]
    y = {"top": margin, "bottom": h - margin - th}[WATERMARK_POSITION.split("-")[0]]
    x, y = x - left, y - top  # compensate for the font's internal bbox offset

    base = im.convert("RGBA")

    if SHADOW_OPACITY > 0:
        shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
        off = max(1, round(font_px * SHADOW_OFFSET))
        ImageDraw.Draw(shadow).text((x + off, y + off), WATERMARK_TEXT, font=font,
                                    fill=(0, 0, 0, round(255 * SHADOW_OPACITY)))
        shadow = shadow.filter(ImageFilter.GaussianBlur(max(1, font_px * SHADOW_BLUR)))
        base = Image.alpha_composite(base, shadow)

    text = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(text).text((x, y), WATERMARK_TEXT, font=font,
                              fill=(255, 255, 255, round(255 * WATERMARK_OPACITY)))
    base = Image.alpha_composite(base, text)

    return base if im.mode == "RGBA" else base.convert("RGB")


def encode(img: Image.Image, quality: int, icc: bytes | None) -> bytes:
    buf = io.BytesIO()
    kwargs = {"format": "WEBP", "quality": quality, "method": 6}
    if icc:
        kwargs["icc_profile"] = icc
    img.save(buf, **kwargs)
    return buf.getvalue()


def optimise(src: Path) -> tuple[bytes, tuple[int, int], int]:
    with Image.open(src) as im:
        icc = im.info.get("icc_profile")
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)  # only ever shrinks
    if WATERMARK_ENABLED:
        im = add_watermark(im)

    # 1) lower quality until it fits
    for q in range(QUALITY, MIN_QUALITY - 1, -5):
        data = encode(im, q, icc)
        if len(data) <= MAX_BYTES:
            return data, im.size, q

    # 2) still too big at minimum quality: shrink dimensions (watermark scales with it)
    while len(data) > MAX_BYTES and max(im.size) > 800:
        w, h = im.size
        im = im.resize((int(w * 0.9), int(h * 0.9)), Image.LANCZOS)
        data = encode(im, MIN_QUALITY, icc)
    return data, im.size, MIN_QUALITY


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="re-convert even if the output is up to date")
    args = ap.parse_args()

    if not SRC_DIR.is_dir():
        print(f"Source folder not found: {SRC_DIR}", file=sys.stderr)
        return 1
    if WATERMARK_POSITION not in {"bottom-right", "bottom-left", "top-right", "top-left", "bottom-center"}:
        print(f"Unknown WATERMARK_POSITION: {WATERMARK_POSITION}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(exist_ok=True)

    sources = sorted(p for p in SRC_DIR.rglob("*")
                     if p.is_file() and p.suffix.lower() in INPUT_EXTS and not p.name.startswith("."))

    # outputs are flattened into images/, so guard against two originals with the same name
    seen: dict[str, Path] = {}
    for s in sources:
        if s.stem in seen:
            print(f"Name clash: '{s}' and '{seen[s.stem]}' would both become {s.stem}.webp", file=sys.stderr)
            return 1
        seen[s.stem] = s

    script_mtime = Path(__file__).stat().st_mtime
    for src in sources:
        dst = OUT_DIR / f"{src.stem}.webp"
        if dst.resolve().is_relative_to(SRC_DIR.resolve()):  # paranoia: never write into originals
            raise RuntimeError(f"Refusing to write inside originals: {dst}")
        if (not args.force and dst.exists()
                and dst.stat().st_mtime >= max(src.stat().st_mtime, script_mtime)):
            print(f"skip  {dst.name} (up to date)")
            continue

        data, size, q = optimise(src)
        tmp = dst.with_suffix(".webp.tmp")
        tmp.write_bytes(data)
        tmp.replace(dst)
        warn = "  ⚠ over limit" if len(data) > MAX_BYTES else ""
        print(f"wrote {dst.name}: {size[0]}x{size[1]}, q{q}, "
              f"{src.stat().st_size // 1024} KB -> {len(data) // 1024} KB{warn}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
