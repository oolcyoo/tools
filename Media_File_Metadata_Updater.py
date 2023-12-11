# %%
# Ree Li 12/10/2023
import os
import json
import subprocess
from PIL import Image, PngImagePlugin
import piexif
from datetime import datetime
import ffmpeg


def update_image_metadata(img_path, formatted_time, exif_dict):
    with Image.open(img_path) as img:
        if img.format == 'JPEG':
            # Update JPEG metadata
            update_image_exif(img_path, exif_dict)
        elif img.format == 'PNG':
            # Add textual metadata for PNG
            meta = PngImagePlugin.PngInfo()
            meta.add_text("Timestamp", formatted_time)
            img.save(img_path, "PNG", pnginfo=meta)
        elif img.format == 'GIF':
            # GIF doesn't support standard metadata, adding a comment instead
            img.save(img_path, "GIF", comment=formatted_time)

def convert_to_degrees(value):
    """Convert a GPS coordinate to degrees/minutes/seconds"""
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = (value - degrees - minutes/60) * 3600
    return degrees, minutes, seconds

def update_image_exif(img_path, exif_dict):
    exif_bytes = piexif.dump(exif_dict)
    img = Image.open(img_path)
    img.save(img_path, "jpeg", exif=exif_bytes)

def update_video_metadata(video_path, metadata):
    try:
        # Extract the current metadata to a file
        meta_export = ffmpeg.input(video_path).output('-', format='ffmetadata').run(capture_stdout=True)
        with open('metadata.txt', 'wb') as f:
            f.write(meta_export[0])
        
        # Append the new metadata
        with open('metadata.txt', 'a') as f:
            f.write(f"\n[CHAPTER]\nTIMEBASE=1/1\nSTART=0\n")
            for key, value in metadata.items():
                f.write(f"{key}={value}\n")
        
        # Apply the new metadata to the video file
        ffmpeg.input(video_path).output(video_path + "_temp", map_metadata='metadata.txt').run()
        
        # Replace the original file with the new file
        os.replace(video_path + "_temp", video_path)
        
        # Clean up the metadata file
        os.remove('metadata.txt')
    except ffmpeg.Error as e:
        print(f"An error occurred while updating metadata for {video_path}: {e}")

def convert_heic_to_jpeg(heic_path, jpeg_path):
    subprocess.run(["magick", "convert", heic_path, jpeg_path])

def convert_jpeg_to_heic(jpeg_path, heic_path):
    subprocess.run(["magick", "convert", jpeg_path, heic_path])

def process_image_file(json_data, media_path):
    formatted_time = datetime.utcfromtimestamp(int(json_data['photoTakenTime']['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')

    # Update EXIF data for images
    lat_degrees, lat_minutes, lat_seconds = convert_to_degrees(json_data['geoData']['latitude'])
    lon_degrees, lon_minutes, lon_seconds = convert_to_degrees(json_data['geoData']['longitude'])
    
    exif_dict = {
        "GPS": {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if json_data['geoData']['latitude'] >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: [(lat_degrees, 1), (lat_minutes, 1), (int(lat_seconds*100), 100)],
            piexif.GPSIFD.GPSLongitudeRef: 'E' if json_data['geoData']['longitude'] >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: [(lon_degrees, 1), (lon_minutes, 1), (int(lon_seconds*100), 100)],
        }
    }

    # Handle different image formats
    if media_path.lower().endswith(('.jpg', '.jpeg', '.heic', '.png', '.gif')):
        with Image.open(media_path) as img:
            if img.format in ['JPEG', 'PNG', 'GIF']:
                if img.format == 'JPEG':
                    # Update JPEG metadata
                    update_image_exif(media_path, exif_dict)
                elif img.format == 'PNG':
                    # Add textual metadata for PNG
                    meta = PngImagePlugin.PngInfo()
                    meta.add_text("Timestamp", formatted_time)
                    img.save(media_path, "PNG", pnginfo=meta)
                elif img.format == 'GIF':
                    # GIF metadata (limited support)
                    img.save(media_path, "GIF", comment=formatted_time)

            elif img.format == 'HEIC':
                # Convert HEIC to JPEG, update metadata, and convert back
                jpeg_path = media_path + '.jpeg'
                convert_heic_to_jpeg(media_path, jpeg_path)
                update_image_exif(jpeg_path, exif_dict)
                convert_jpeg_to_heic(jpeg_path, media_path)
                os.remove(jpeg_path)

def process_video_file(json_data, media_path):
    # Update metadata for videos
    formatted_time = datetime.utcfromtimestamp(int(json_data['photoTakenTime']['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')
    metadata = {
        'creation_time': formatted_time,
        'location': f"+{json_data['geoData']['latitude']}+{json_data['geoData']['longitude']}/",
    }
    update_video_metadata(media_path, metadata)


directory = "TP"

for filename in os.listdir(directory):
    if filename.endswith('.json'):
        json_path = os.path.join(directory, filename)
        base_filename = filename.rsplit('.', 1)[0]
        
        with open(json_path, 'r') as f:
            json_data = json.load(f)
        
        # Include '.PNG' and '.GIF' in the extensions
        for ext in ('.JPG', '.JPEG', '.HEIC', '.MOV', '.MP4', '.PNG', '.GIF'):
            media_path = os.path.join(directory, base_filename + ext)
            if os.path.exists(media_path):
                if media_path.lower().endswith(('.jpg', '.jpeg', '.heic', '.png', '.gif')):
                    process_image_file(json_data, media_path)
                elif media_path.lower().endswith(('.mov', '.mp4')):
                    process_video_file(json_data, media_path)
                break

print("Metadata update process completed.")

