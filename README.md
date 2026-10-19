# jpg-to-png-converter

A small command-line tool that batch-converts JPG/JPEG images to PNG, built on [Pillow](https://python-pillow.org/).

It handles the details a naive conversion gets wrong:

- **Correct orientation.** Phone and camera photos often store rotation as an EXIF flag rather than rotating the pixels. The tool applies that flag, so rotated photos come out upright.
- **Safe writes.** Each PNG is written to a temporary file and renamed into place, so an interrupted run never leaves a half-written image behind.
- **Originals kept by default.** JPGs are deleted only when you pass `--delete`, and only after their PNG has been saved successfully.
- **Keeps going on bad files.** A corrupt or unreadable image is reported and skipped; the rest of the batch still runs.
- **Sensible color handling.** Grayscale images stay grayscale; CMYK and other modes are converted to RGB.

## Installation

Requires Python 3.8 or newer. Clone or download this repository, then install the one dependency:

```bash
pip install -r requirements.txt
```

## Usage

```bash
python convert.py [folder] [options]
```

| Option | Effect |
|---|---|
| `folder` | Folder to process (default: current folder) |
| `-r`, `--recursive` | Also process subfolders |
| `--delete` | Delete each original JPG after it converts successfully |
| `--overwrite` | Replace PNGs that already exist (default: skip them) |
| `--dry-run` | List what would be converted without changing anything |

### Examples

```bash
# Preview what would happen in a folder and all its subfolders
python convert.py photos/ -r --dry-run

# Convert, keeping the original JPGs
python convert.py photos/

# Convert and remove the originals
python convert.py photos/ -r --delete
```

The script prints one line per file and a summary at the end. It exits with code `1` if any file failed to convert and `2` if the folder doesn't exist, so it can be used in other scripts.

## Things to know

- **PNG doesn't restore quality.** JPG compression loss is already baked in; converting to PNG preserves the image exactly as it is now, at a larger file size (often several times larger). Convert when a tool or workflow requires PNG.
- **EXIF metadata is not carried over.** Capture date, camera details, and GPS location are dropped from the PNG. Keep the originals if you need that information.

## License

[MIT](LICENSE)
