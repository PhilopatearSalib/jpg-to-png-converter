#!/usr/bin/env python3
"""Batch-convert JPG/JPEG images to PNG.

Usage examples:
    python convert.py                      # convert JPGs in the current folder, keep originals
    python convert.py photos/ -r           # include subfolders
    python convert.py photos/ --delete     # remove each JPG after a successful conversion
    python convert.py photos/ --dry-run    # show what would happen, change nothing
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from PIL import Image, ImageOps

JPG_EXTS = {".jpg", ".jpeg"}


def find_jpgs(folder: Path, recursive: bool) -> list[Path]:
    """Return JPG/JPEG files in `folder` (optionally recursive), sorted by path."""
    candidates = folder.rglob("*") if recursive else folder.glob("*")
    return sorted(p for p in candidates if p.is_file() and p.suffix.lower() in JPG_EXTS)


def convert_one(jpg: Path, png: Path) -> None:
    """Convert a single JPG to PNG.

    - Applies the EXIF orientation flag so rotated photos come out upright.
    - Keeps grayscale images grayscale; converts everything else (e.g. CMYK) to RGB.
    - Writes to a temporary file and renames it into place, so a crash never
      leaves a half-written PNG behind.
    """
    tmp = png.with_name(png.name + ".tmp")
    try:
        with Image.open(jpg) as im:
            im = ImageOps.exif_transpose(im)
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            im.save(tmp, "PNG", optimize=True)
        os.replace(tmp, png)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch-convert JPG/JPEG images to PNG.",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        type=Path,
        help="folder containing the images (default: current folder)",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="also process subfolders",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="delete each original JPG after it converts successfully",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace PNGs that already exist (default: skip them)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list what would be converted without changing any files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    folder: Path = args.folder

    if not folder.is_dir():
        print(f"Error: '{folder}' is not a folder.", file=sys.stderr)
        return 2

    converted = deleted = skipped = failed = 0

    for jpg in find_jpgs(folder, args.recursive):
        png = jpg.with_suffix(".png")
        rel = jpg.relative_to(folder)

        if png.exists() and not args.overwrite:
            print(f"skip     {rel}  (PNG already exists)")
            skipped += 1
            continue

        if args.dry_run:
            action = "convert+delete" if args.delete else "convert"
            print(f"{action:<8} {rel}")
            continue

        try:
            convert_one(jpg, png)
        except Exception as e:  # keep going on bad files
            print(f"FAILED   {rel}: {e}", file=sys.stderr)
            failed += 1
            continue

        converted += 1
        print(f"ok       {rel}")

        if args.delete:
            jpg.unlink()
            deleted += 1

    summary = (
        f"\nDone. Converted: {converted}, Deleted JPGs: {deleted}, "
        f"Skipped: {skipped}, Failed: {failed}"
    )
    if args.dry_run:
        summary += "  (dry run, nothing changed)"
    print(summary)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
