import os
import json
import argparse
from ImageSelector import ImageSelector

def main(transforms_path, target_count, output_file, num_groups=None, scalar=None, pretend=False):
    # Determine whether we're working with a directory or a specific JSON file
    if os.path.isdir(transforms_path):
        main_directory = transforms_path
        json_path = os.path.join(main_directory, "transforms.json")
    else:
        json_path = transforms_path
        main_directory = os.path.dirname(json_path)

    # Load transform data from the provided JSON path
    with open(json_path, "r") as file:
        transforms_data = json.load(file)

    frames = sorted(transforms_data["frames"], key=lambda x: x["colmap_im_id"])
    images = [os.path.join(main_directory, frame["file_path"]) for frame in frames]

    if target_count is None:
        total_images = len(images)
        target_count = int(total_images * (args.target_percentage / 100))

    selector = ImageSelector(images)
    selected_images = selector.filter_sharpest_images(target_count, num_groups, scalar)

    new_frames = [frame for frame in transforms_data["frames"] if os.path.join(main_directory, frame["file_path"]) in selected_images]
    transforms_data["frames"] = new_frames

    # If pretend mode, just print what would be done
    if pretend:
        print(f"Would have retained {len(selected_images)} sharpest images. Would have saved to {output_file} (--pretend)")
    else:
        if not args.yes:
            answer = input(f"About to remove all but {len(selected_images)} images from '{output_file}', continue? [y/N]: ").lower()
            if answer not in ["y", "yes"]:
                print("Aborting.")
                return

        output_path = os.path.join(os.getcwd(), output_file)
        with open(output_path, "w") as file:
            json.dump(transforms_data, file, indent=4)
        print(f"Retained {len(selected_images)} sharpest images. Saved to '{output_path}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Select and retain only the sharpest images from a COLMAP output.")
    parser.add_argument('--transforms_path', required=True, help="Path to the main COLMAP output directory or the transforms.json file.")
    group_target = parser.add_mutually_exclusive_group(required=True)
    group_target.add_argument('--target_count', type=int, help="Target number of images to retain.")
    group_target.add_argument('--target_percentage', type=float, help="Target percentage of top quality images to retain. I.e. --target_percentage 95 removes the 5% worst quality images.")
    parser.add_argument('--output_file', default=None, help="Path to save the output JSON. If not specified, the default is transforms_filtered.json in the same directory as the transforms file.")
    group_division = parser.add_mutually_exclusive_group()
    group_division.add_argument('--groups', type=int, help="Specify the number of groups to divide the images into.")
    group_division.add_argument('--scalar', type=int, help="Specify the scalar value to determine group division if num_groups is not provided.")

    parser.add_argument('--pretend', action='store_true', help="Pretend mode. Do not write or delete anything, just show what would have been done.")
    parser.add_argument('--yes', '-y', action='store_true', help="Automatically answer 'yes' to all prompts and execute actions.")

    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = os.path.join(os.path.dirname(args.transforms_path), "transforms_filtered.json")

    main(args.transforms_path, args.target_count, args.output_file, args.num_groups, args.scalar, args.pretend)

