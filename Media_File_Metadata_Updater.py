# Ree Li 12/10/2023
import argparse
import json
import os
import subprocess
from datetime import datetime

import ffmpeg
import piexif
from PIL import Image, PngImagePlugin


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".heic", ".png", ".gif")
VIDEO_EXTENSIONS = (".mov", ".mp4")
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS


def update_image_metadata(img_path, formatted_time, exif_dict):
    with Image.open(img_path) as img:
        if img.format == "JPEG":
            update_image_exif(img_path, exif_dict)
        elif img.format == "PNG":
            meta = PngImagePlugin.PngInfo()
            meta.add_text("Timestamp", formatted_time)
            img.save(img_path, "PNG", pnginfo=meta)
        elif img.format == "GIF":
            img.save(img_path, "GIF", comment=formatted_time)


def convert_to_degrees(value):
    """Convert a GPS coordinate to degrees/minutes/seconds."""
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = (value - degrees - minutes / 60) * 3600
    return degrees, minutes, seconds


def update_image_exif(img_path, exif_dict):
    exif_bytes = piexif.dump(exif_dict)
    img = Image.open(img_path)
    img.save(img_path, "jpeg", exif=exif_bytes)


def update_video_metadata(video_path, metadata):
    metadata_path = video_path + ".metadata.txt"
    temp_path = video_path + "_temp"
    try:
        meta_export = ffmpeg.input(video_path).output("-", format="ffmetadata").run(capture_stdout=True)
        with open(metadata_path, "wb") as f:
            f.write(meta_export[0])

        with open(metadata_path, "a") as f:
            f.write("\n[CHAPTER]\nTIMEBASE=1/1\nSTART=0\n")
            for key, value in metadata.items():
                f.write(f"{key}={value}\n")

        ffmpeg.input(video_path).output(temp_path, map_metadata=metadata_path).run()
        os.replace(temp_path, video_path)
    except ffmpeg.Error as e:
        print(f"An error occurred while updating metadata for {video_path}: {e}")
    finally:
        if os.path.exists(metadata_path):
            os.remove(metadata_path)


def convert_heic_to_jpeg(heic_path, jpeg_path):
    subprocess.run(["magick", "convert", heic_path, jpeg_path], check=True)


def convert_jpeg_to_heic(jpeg_path, heic_path):
    subprocess.run(["magick", "convert", jpeg_path, heic_path], check=True)


def build_exif_dict(json_data):
    lat = json_data["geoData"]["latitude"]
    lon = json_data["geoData"]["longitude"]
    lat_degrees, lat_minutes, lat_seconds = convert_to_degrees(abs(lat))
    lon_degrees, lon_minutes, lon_seconds = convert_to_degrees(abs(lon))

    return {
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: "N" if lat >= 0 else "S",
            piexif.GPSIFD.GPSLatitude: [(lat_degrees, 1), (lat_minutes, 1), (int(lat_seconds * 100), 100)],
            piexif.GPSIFD.GPSLongitudeRef: "E" if lon >= 0 else "W",
            piexif.GPSIFD.GPSLongitude: [(lon_degrees, 1), (lon_minutes, 1), (int(lon_seconds * 100), 100)],
        }
    }


def process_image_file(json_data, media_path):
    formatted_time = datetime.utcfromtimestamp(
        int(json_data["photoTakenTime"]["timestamp"])
    ).strftime("%Y-%m-%d %H:%M:%S")
    exif_dict = build_exif_dict(json_data)

    with Image.open(media_path) as img:
        if img.format in ["JPEG", "PNG", "GIF"]:
            update_image_metadata(media_path, formatted_time, exif_dict)
        elif img.format == "HEIC":
            jpeg_path = media_path + ".jpeg"
            convert_heic_to_jpeg(media_path, jpeg_path)
            update_image_exif(jpeg_path, exif_dict)
            convert_jpeg_to_heic(jpeg_path, media_path)
            os.remove(jpeg_path)


def process_video_file(json_data, media_path):
    formatted_time = datetime.utcfromtimestamp(
        int(json_data["photoTakenTime"]["timestamp"])
    ).strftime("%Y-%m-%d %H:%M:%S")
    metadata = {
        "creation_time": formatted_time,
        "location": f"+{json_data['geoData']['latitude']}+{json_data['geoData']['longitude']}/",
    }
    update_video_metadata(media_path, metadata)


def find_matching_media(directory, json_base_filename):
    candidates = {json_base_filename.lower()}
    for ext in MEDIA_EXTENSIONS:
        candidates.add((json_base_filename + ext).lower())

    for filename in os.listdir(directory):
        if filename.lower() in candidates and filename.lower().endswith(MEDIA_EXTENSIONS):
            return os.path.join(directory, filename)
    return None


def update_directory_metadata(directory):
    for filename in os.listdir(directory):
        if not filename.endswith(".json"):
            continue

        json_path = os.path.join(directory, filename)
        json_base_filename = filename.rsplit(".", 1)[0]
        media_path = find_matching_media(directory, json_base_filename)
        if not media_path:
            continue

        with open(json_path, "r") as f:
            json_data = json.load(f)

        if media_path.lower().endswith(IMAGE_EXTENSIONS):
            process_image_file(json_data, media_path)
        elif media_path.lower().endswith(VIDEO_EXTENSIONS):
            process_video_file(json_data, media_path)


def parse_args():
    parser = argparse.ArgumentParser(description="Update media metadata from matching JSON files.")
    parser.add_argument(
        "directory",
        nargs="?",
        default="TP",
        help="Directory containing media files and matching JSON metadata files.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    update_directory_metadata(args.directory)
    print("Metadata update process completed.")


if __name__ == "__main__":
    main()
