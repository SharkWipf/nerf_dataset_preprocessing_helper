import cv2
import os
import json
import argparse
from tqdm import tqdm

def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def retain_sharpest_per_group(group_sizes, image_fm, offset=0):
    selected_images = []
    offset_index = 0 if not offset else group_sizes[0] // 2

    for size in group_sizes:
        end_idx = offset_index + size
        group = image_fm[offset_index:end_idx]
        group.sort(reverse=True)
        sharpest_img = group[0][1]
        selected_images.append(sharpest_img)
        offset_index = end_idx

    return selected_images

def main(transforms_path, target_count, use_two_pass_approach, output_file, force_grouping, force_ungrouped):
    # Check for contradicting force flags
    if force_grouping and force_ungrouped:
        print("You cannot force both grouping and ungrouped. Choose one.")
        return

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
    image_fm = [(variance_of_laplacian(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)), os.path.relpath(img, main_directory)) for img in tqdm(images)]

    split = len(images) / target_count
    ratio = target_count / len(images)
    formatted_ratio = "{:.2%}".format(ratio)
    print(f"Requested {target_count} out of {len(images)} images ({formatted_ratio}, 1 in {split}).")

    if not force_grouping and split < 2 or force_ungrouped:
        if not force_ungrouped:
            print("Warning: Ratio is < 2, falling back to ungrouped approach (use --force_grouping to override).")
        print("Running ungrouped. This may cause an uneven distribution of data.")
        image_fm.sort()
        selected_images = [img[1] for img in image_fm[-target_count:]]
    else:
        if force_grouping and split < 2:
            print("Warning: Forcibly grouping despite a ratio of < 2. This may not work as expected.")
            if(use_two_pass_approach):
                print("Cannot use two-pass with a ratio of <2. Falling back to single pass.")
                use_two_pass_approach = False
        if use_two_pass_approach:
            print("Using two-pass grouping (potentially better distribution, possibly slightly worse quality).")
        else:
            print("Using single-pass grouping (potentially worse distribution, possibly slightly higher quality).")

        full_groups = len(images) // target_count
        remaining_images = len(images) % target_count
        group_sizes = [full_groups] * target_count

        for i in range(remaining_images):
            group_sizes[i] += 1

        selected_images = retain_sharpest_per_group(group_sizes, image_fm)

        if use_two_pass_approach:
            selected_images_second_pass = retain_sharpest_per_group(group_sizes, image_fm, offset=0.5)
            combined_selection = list(zip(selected_images, selected_images_second_pass))

            selected_images = []
            for img1, img2 in combined_selection:
                center_idx = (image_fm.index((next(item for item in image_fm if item[1] == img1))) +
                              image_fm.index((next(item for item in image_fm if item[1] == img2)))) / 2

                if abs(image_fm.index((next(item for item in image_fm if item[1] == img1))) - center_idx) < \
                        abs(image_fm.index((next(item for item in image_fm if item[1] == img2))) - center_idx):
                    selected_images.append(img1)
                else:
                    selected_images.append(img2)

    new_frames = [frame for frame in transforms_data["frames"] if frame["file_path"] in selected_images]
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

    # If output_file wasn't specified, default to transforms_filtered.json in the same directory as the transforms file.
    if args.output_file is None:
        args.output_file = os.path.join(os.path.dirname(args.transforms_path), "transforms_filtered.json")

    main(args.transforms_path, args.target_count, args.two_pass, args.output_file, args.force_grouping, args.force_ungrouped)
