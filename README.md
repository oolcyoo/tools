
# Media File Metadata Updater

This script updates the metadata of media files (images and videos) using associated JSON files containing timestamp and geolocation data.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Pillow (PIL Fork) Library
- Piexif Library
- FFmpeg
- ImageMagick

You can install the required Python libraries using pip:

```bash
pip install pillow piexif
```

FFmpeg and ImageMagick need to be installed and available in your system's PATH. Refer to the respective documentation for installation instructions:

- [FFmpeg Installation Guide](https://ffmpeg.org/download.html)
- [ImageMagick Installation Guide](https://imagemagick.org/script/download.php)

## Supported File Formats

The script supports the following media file formats:

- Images: JPEG, PNG, GIF, HEIC
- Videos: MOV, MP4

## How to Use

1. Place the script in a directory containing your media files and the corresponding JSON files.
2. The JSON files should have the same base name as the media files, with an additional `.json` extension.
3. Open the script in a text editor and modify the `directory` variable to the path containing your media and JSON files.
4. Run the script from the terminal:

```bash
python3 media_metadata_updater.py
```

## Notes

- The script reads the `photoTakenTime` and `geoData` from the JSON files and updates the media files' metadata accordingly.
- For images, it updates the EXIF data (for JPEG and HEIC) and adds textual information (for PNG and GIF).
- For videos, it embeds the timestamp and geolocation into the video metadata.
- The script converts HEIC images to JPEG to update the EXIF data and then converts them back to HEIC.

## Troubleshooting

- Ensure that all dependencies are correctly installed and configured.
- Verify that the JSON files are correctly formatted and contain the necessary fields for the script to function.
- If the metadata does not appear updated, use dedicated metadata viewers to verify the changes, as operating system file properties may not reflect all metadata updates.

## Caution

- The script overwrites the original media files with the updated metadata. It is recommended to back up your media files before running the script.
- Ensure that FFmpeg and ImageMagick commands are allowed to execute by your system's security settings.
