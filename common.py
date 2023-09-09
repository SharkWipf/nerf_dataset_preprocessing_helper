import cv2
import os
from tqdm import tqdm
from graphlib import draw_graph

def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()

def generate_deleted_images_graph(all_images, selected_images):
    bins = 100
    step = len(all_images) // bins
    percentages = []

    for i in range(bins):
        start_idx = i * step
        end_idx = (i + 1) * step if i != bins - 1 else len(all_images)
        current_bin = all_images[start_idx:end_idx]
        deleted_count = sum(1 for img in current_bin if img not in selected_images)
        avg = deleted_count / len(current_bin)
        percentages.append(avg * 100)

    draw_graph(percentages, "Distribution of Deleted Images (Not super useful for grouped mode)")

def generate_quality_graph(image_fm):
    draw_graph([quality for quality, _ in image_fm], "Distribution of Image Quality")

def retain_sharpest_per_group(group_sizes, image_fm, offset=0):
    selected_images = []
    offset_index = int(offset) if not offset else group_sizes[0] // 2

    for size in group_sizes:
        end_idx = offset_index + size
        group = sorted(image_fm[offset_index:end_idx], reverse=True)
        sharpest_img = group[0][1]
        selected_images.append(sharpest_img)
        offset_index = end_idx

    return selected_images

def filter_sharpest_images(images, target_count, use_two_pass_approach, force_grouped, force_ungrouped):
    image_fm = [(variance_of_laplacian(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)), img) for img in tqdm(images)]
    split = len(images) / target_count
    ratio = target_count / len(images)
    formatted_ratio = "{:.1%}".format(ratio)
    print(f"Requested {target_count} out of {len(images)} images ({formatted_ratio}, 1 in {split:.2f}).")

    if not force_grouped and split < 2 or force_ungrouped:
        if not force_ungrouped:
            print("Warning: Ratio is < 2, falling back to ungrouped approach (use --force_grouped to override).")
        print("Running ungrouped. This may cause an uneven distribution of data.")
        image_fm_unsorted = image_fm.copy()
        image_fm.sort()
        selected_images = [img[1] for img in image_fm[-target_count:]]

        print()
        generate_deleted_images_graph(images, selected_images)
        generate_quality_graph(image_fm_unsorted)

        return selected_images

    else:
        if force_grouped and split < 2:
            print("Warning: Forcibly grouping despite a ratio of < 2. This may not work as expected.")
            if(use_two_pass_approach):
                print("Cannot use two-pass with a ratio of <2. Falling back to single pass.")
                use_two_pass_approach = False
        if use_two_pass_approach:
            print("Using two-pass grouping (potentially better distribution, possibly slightly worse quality).")
        else:
            print("Using single-pass grouping (potentially worse distribution, possibly slightly higher quality).")

        # Here we will try to distribute "leftovers" over all groups as evenly as possible.
        num_images = len(images)
        group_sizes = [0] * target_count

        # The ideal number of images per group
        ideal_per_group = num_images / target_count
        accumulated_error = 0.0

        for i in range(target_count):
            # Add the full groups worth
            group_sizes[i] = int(ideal_per_group)
            # Accumulate the error
            accumulated_error += ideal_per_group - group_sizes[i]

            # Check if the accumulated error has reached a whole number
            while accumulated_error >= 1.0:
                group_sizes[i] += 1
                accumulated_error -= 1.0

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

        print()
        generate_deleted_images_graph(images, selected_images)
        generate_quality_graph(image_fm)

        return selected_images
