import os
import json
import argparse
from common import filter_sharpest_images

def main(transforms_path, target_count, use_two_pass_approach, output_file, force_grouping, force_ungrouped):
    if os.path.isdir(transforms_path):
        main_directory = transforms_path
        json_path = os.path.join(main_directory, "transforms.json")
    else:
        json_path = transforms_path
        main_directory = os.path.dirname(json_path)

    with open(json_path, "r") as file:
        transforms_data = json.load(file)

    frames = sorted(transforms_data["frames"], key=lambda x: x["colmap_im_id"])
    images = [os.path.join(main_directory, frame["file_path"]) for frame in frames]

    selected_images = filter_sharpest_images(images, target_count, use_two_pass_approach, force_grouping, force_ungrouped)
    new_frames = [frame for frame in transforms_data["frames"] if os.path.join(main_directory, frame["file_path"]) in selected_images]
    transforms_data["frames"] = new_frames

    output_path = os.path.join(os.getcwd(), output_file)
    with open(output_path, "w") as file:
        json.dump(transforms_data, file, indent=4)

    print(f"Retained {len(selected_images)} sharpest images. Saved to {output_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Select and retain only the sharpest images from a COLMAP output.")
    parser.add_argument('--transforms_path', required=True, help="Path to the main COLMAP output directory or the transforms.json file.")
    parser.add_argument('--target_count', type=int, required=True, help="Target number of images to retain.")
    parser.add_argument('--output_file', default=None, help="Path to save the output JSON. If not specified, the default is transforms_filtered.json in the same directory as the transforms file.")
    parser.add_argument('--two_pass', action='store_true', help="Use a two-pass approach for image selection, aiming for a better distribution of frames, potentially at a slight quality cost.")
    parser.add_argument('--force_grouping', action='store_true', help="Force the program to use the grouped approach regardless of image count.")
    parser.add_argument('--force_ungrouped', action='store_true', help="Force the program to use the non-grouped approach regardless of image count.")

    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = os.path.join(os.path.dirname(args.transforms_path), "transforms_filtered.json")

    main(args.transforms_path, args.target_count, args.two_pass, args.output_file, args.force_grouping, args.force_ungrouped)
