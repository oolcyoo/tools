# Tools

Small personal utility scripts for media cleanup and PDF handling.

## Utilities

| File | Purpose |
| --- | --- |
| `Media_File_Metadata_Updater.py` | Updates image/video metadata from matching JSON sidecar files, such as timestamp and GPS data exported with media archives. |
| `combine_pdfs.py` | Combines all PDFs in a directory into one output PDF. |
| `combine.ipynb` | Original notebook version of the PDF combiner. |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The media metadata updater also expects these command-line tools to be installed and available on `PATH`:

- FFmpeg
- ImageMagick, for HEIC conversion through `magick convert`

## Media Metadata Updater

The updater expects media files and matching JSON files in the same directory. The JSON files should include `photoTakenTime` and `geoData` fields.

```bash
python3 Media_File_Metadata_Updater.py path/to/media-directory
```

If no directory is passed, it uses `TP` for compatibility with the original script.

Supported media types:

- Images: JPEG, PNG, GIF, HEIC
- Videos: MOV, MP4

The script writes metadata back to the media files, so run it on a copy of important files first.

## PDF Combiner

```bash
python3 combine_pdfs.py path/to/pdf-directory -o combined.pdf
```

The script combines PDFs in sorted filename order.

## Notes

- `TP/`, `M6P/`, generated PDFs, temporary metadata files, virtual environments, and notebook checkpoints are ignored by `.gitignore`.
- The notebook is kept as the original quick experiment; `combine_pdfs.py` is the reusable command-line version.
