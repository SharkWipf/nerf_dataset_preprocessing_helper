import os
import argparse
import shutil
import subprocess
from ImageSelector import ImageSelector

def extract_frames(input_vid, output_path):
    if not args.yes:
        answer = input(f"About to extract all frames from '{input_vid}' into '{output_path}' (even with --pretend!). This folder will persist unless manually removed. Continue? [y/N]: ").lower()
        if answer not in ["y", "yes"]:
            print("Aborting.")
            exit()
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    cmd = [
        'ffmpeg',
        '-i', input_vid,
        '-vsync', 'vfr',
        '-v', 'quiet',
        '-stats',
        '-q:v', '1',  # Use highest quality for JPEG
        os.path.join(output_path, 'frame%05d.jpg')
    ]
    subprocess.run(cmd)

def main(input_path, output_path, target_count, groups=None, scalar=None):
    # Check if input_path is a folder or video
    if os.path.isdir(input_path):
        images = [os.path.join(input_path, img) for img in os.listdir(input_path) if img.endswith('.jpg')]
        images.sort()
    else:
        extract_frames(input_path, output_path)
        images = [os.path.join(output_path, img) for img in os.listdir(output_path) if img.endswith('.jpg')]
        images.sort()

    if target_count is None:
        total_images = len(images)
        target_count = int(total_images * (args.target_percentage / 100))

    selector = ImageSelector(images)
    selected_images = selector.filter_sharpest_images(target_count, groups, scalar)

    if args.pretend:
        print(f"Would have retained {len(selected_images)} sharpest images. (--pretend)")
        if not os.path.isdir(input_path):
            print(f"Warning: Folder '{output_path}' persists, with all extracted frames in it.")
        return

    if not args.yes:
        if not os.path.isdir(input_path):
            print(f"Folder '{output_path}' will persist, with all extracted frames in it. Responding 'y' will prune it down to the desired output, but responding 'n' will keep it as-is, with all extracted frames.")
        answer = input(f"About to delete all but {len(selected_images)} sharpest images. Continue? [y/N]: ").lower()
        if answer not in ["y", "yes"]:
            print("Aborting.")
            return

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if os.path.isdir(input_path) and os.path.normcase(os.path.abspath(os.path.normpath(input_path))) != os.path.normcase(os.path.abspath(os.path.normpath(output_path))):
        print(os.path.normcase(os.path.abspath(os.path.normpath(input_path))))
        print(os.path.normcase(os.path.abspath(os.path.normpath(output_path))))
        for img in selected_images:
            new_location = os.path.join(output_path, os.path.basename(img))
            shutil.copy2(img, new_location)
    else:
        for img in images:
            if img not in selected_images:
                os.remove(img)

    print(f"Retained {len(selected_images)} sharpest images.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Select and retain only the sharpest frames from a video or folder of images.")
    parser.add_argument('--input_path', required=True, help="Path to the input_path video or folder of images.")
    parser.add_argument('--output_path', help="Directory to save the preserved images. Mandatory for video, optional for images. Will delete images in-place if not specified.")
    group_target = parser.add_mutually_exclusive_group(required=True)
    group_target.add_argument('--target_count', type=int, help="Target number of images to retain.")
    group_target.add_argument('--target_percentage', type=float, help="Target percentage of top quality images to retain. I.e. --target_percentage 95 removes the 5%% worst quality images.")
    group_division = parser.add_mutually_exclusive_group()
    group_division.add_argument('--groups', type=int, help="Specify the number of groups to divide the images into.")
    group_division.add_argument('--scalar', type=int, help="Specify the scalar value to determine group division if groups is not provided.")
    parser.add_argument('--pretend', action='store_true', help="Pretend mode. Do not delete anything, just show what would have been deleted. Warning: Will still create and populate the output dir if input_path is a video!")
    parser.add_argument('--yes', '-y', action='store_true', help="Automatically answer 'yes' to all prompts and execute actions.")

    args = parser.parse_args()

    if not os.path.isdir(args.input_path) and not args.output_path:
        parser.error("The --output_path argument is mandatory when the input_path is a video.")
    elif not args.output_path or (os.path.normcase(os.path.abspath(os.path.normpath(args.input_path))) is os.path.normcase(os.path.abspath(os.path.normpath(args.output_path)))):
        args.output_path = args.input_path

    main(args.input_path, args.output_path, args.target_count, args.groups, args.scalar)
