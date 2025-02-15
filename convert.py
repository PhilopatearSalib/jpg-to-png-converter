from pathlib import Path
from PIL import Image

# Put this script INSIDE the images folder, then run it.
# It converts .jpg/.jpeg -> .png in the same folder, then deletes the original JPG
def main(recursive: bool = False):
    folder = Path.cwd()
    pattern = "**/*" if recursive else "*"
    exts = {".jpg", ".jpeg"}

    converted = 0
    deleted = 0
    skipped = 0

    for jpg in folder.glob(pattern):
        if not (jpg.is_file() and jpg.suffix.lower() in exts):
            continue

        png = jpg.with_suffix(".png")
        if png.exists():
            skipped += 1
            continue

        try:
            with Image.open(jpg) as im:
                im.convert("RGB").save(png, "PNG", optimize=True)
            converted += 1

            jpg.unlink()  # delete original jpg
            deleted += 1
        except Exception as e:
            print(f"Failed on {jpg.name}: {e}")

    print(f"Done. Converted: {converted}, Deleted JPGs: {deleted}, Skipped (PNG existed): {skipped}")

if __name__ == "__main__":
    main(recursive=False)  # set True to include subfolders
