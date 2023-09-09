import os
import json
import argparse
import shutil
import subprocess
from common import filter_sharpest_images

def extract_frames(input_vid, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    cmd = [
        'ffmpeg',
        '-i', input_vid,
        '-vsync', 'vfr',
        '-q:v', '1',  # Use highest quality for JPEG
        os.path.join(output_dir, 'frame%05d.jpg')
    ]
    subprocess.run(cmd)

def main(input_path, output_dir, target_count, use_two_pass_approach, force_grouped, force_ungrouped, pretend):
    # Check if input_path is a folder or video
    if os.path.isdir(input_path):
        images = [os.path.join(input_path, img) for img in os.listdir(input_path) if img.endswith('.jpg')]
        images.sort()
    else:
        extract_frames(input_path, output_dir)
        images = [os.path.join(output_dir, img) for img in os.listdir(output_dir) if img.endswith('.jpg')]
        images.sort()

    if target_count is None:
        total_images = len(images)
        target_count = int(total_images * (args.target_percentage / 100))

    selected_images = filter_sharpest_images(images, target_count, use_two_pass_approach, force_grouped, force_ungrouped)

    preserved_images_dir = output_dir if output_dir else input_path

    for img in images:
        if img not in selected_images:
            if not pretend:
                # Only remove the non-preserved images if there isn't a distinct output directory
                if not output_dir or os.path.dirname(img) == output_dir:
                    os.remove(img)
        else:
            # Check if the output directory is set and distinct from the source
            if output_dir and os.path.dirname(img) != output_dir:  
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                new_location = os.path.join(preserved_images_dir, os.path.basename(img))
                shutil.copy2(img, new_location)  # Using copy2 to preserve metadata

    print(f"Retained {len(selected_images)} sharpest images.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Select and retain only the sharpest frames from a video or folder of images.")

    parser.add_argument('--input', required=True, help="Path to the input video or folder of images.")
    parser.add_argument('--output_dir', help="Directory to save the preserved images. Mandatory for video, optional for images. Will delete images in-place if not specified.")

    group_target = parser.add_mutually_exclusive_group(required=True)
    group_target.add_argument('--target_count', type=int, help="Target number of images to retain.")
    group_target.add_argument('--target_percentage', type=float, help="Target percentage of top quality images to retain. Value should be between 0 and 100.")

    parser.add_argument('--two_pass', action='store_true', help="Use a two-pass approach for image selection, aiming for a better distribution of frames, potentially at a slight quality cost.")

    group_forcing = parser.add_mutually_exclusive_group()
    group_forcing.add_argument('--force_grouped', action='store_true', help="Force the program to use the grouped approach regardless of image count.")
    group_forcing.add_argument('--force_ungrouped', action='store_true', help="Force the program to use the non-grouped approach regardless of image count.")

    parser.add_argument('--pretend', action='store_true', help="Pretend mode. Do not delete anything, just show what would have been deleted.")

    args = parser.parse_args()

    if not os.path.isdir(args.input) and not args.output_dir:  # Meaning input is a video
        parser.error("The --output_dir argument is mandatory when the input is a video.")

    main(args.input, args.output_dir, args.target_count, args.two_pass, args.force_grouped, args.force_ungrouped, args.pretend)

