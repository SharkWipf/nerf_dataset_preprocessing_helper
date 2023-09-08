import cv2
import os
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

def filter_sharpest_images(images, target_count, use_two_pass_approach, force_grouping, force_ungrouped):
    image_fm = [(variance_of_laplacian(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)), img) for img in tqdm(images)]

    split = len(images) / target_count
    ratio = target_count / len(images)
    formatted_ratio = "{:.2%}".format(ratio)
    print(f"Requested {target_count} out of {len(images)} images ({formatted_ratio}, 1 in {split}).")

    if not force_grouping and split < 2 or force_ungrouped:
        if not force_ungrouped:
            print("Warning: Ratio is < 2, falling back to ungrouped approach (use --force_grouping to override).")
        print("Running ungrouped. This may cause an uneven distribution of data.")
        image_fm.sort()
        return [img[1] for img in image_fm[-target_count:]]

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

        return selected_images
