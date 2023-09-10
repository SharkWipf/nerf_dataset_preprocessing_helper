import cv2
from tqdm import tqdm
from graphlib import draw_graph

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

    draw_graph(percentages, "Distribution of to-be-deleted images")


def generate_quality_graph(image_fm):
    draw_graph([quality for quality, _ in image_fm], "Distribution of image quality")


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


def distribute_evenly(total, num_of_groups):
    ideal_per_group = total / num_of_groups
    accumulated_error = 0.0
    distribution = [0] * num_of_groups
    
    for i in range(num_of_groups):
        distribution[i] = int(ideal_per_group)
        accumulated_error += ideal_per_group - distribution[i]
        
        while accumulated_error >= 1.0:
            distribution[i] += 1
            accumulated_error -= 1.0

    return distribution, ideal_per_group


def filter_sharpest_images(images, target_count, group_count=None, scalar=1):
    if scalar is None:
        scalar = 1
    if group_count is None:  # If group_count is not provided, use scalar to determine it
        group_count = target_count // (2 ** (scalar - 1))
        group_count = max(1, group_count)  # Ensure it's at least 1 to avoid dividing by zero

    # Calculate ratio and print details
    split = len(images) / target_count
    ratio = target_count / len(images)
    formatted_ratio = "{:.1%}".format(ratio)
    print(f"Requested {target_count} out of {len(images)} images ({formatted_ratio}, 1 in {split:.1f}).")
    print("Calculating image sharpness...")
    image_fm = [(variance_of_laplacian(cv2.cvtColor(cv2.imread(img), cv2.COLOR_BGR2GRAY)), img) for img in tqdm(images)]

    # Determine group sizes
    group_sizes, ideal_total_images_per_group = distribute_evenly(len(images), group_count)
    images_per_group_list, ideal_selected_images_per_group = distribute_evenly(target_count, group_count)

    print(f"Selecting {target_count} image{'s' if target_count != 1 else ''} across {group_count} group{'s' if group_count != 1 else ''}, with total ~{ideal_total_images_per_group:.1f} image{'s' if ideal_total_images_per_group != 1 else ''} per group and selecting ~{ideal_selected_images_per_group:.1f} image{'s' if ideal_selected_images_per_group != 1 else ''} per group (scalar {scalar}).")

    # Determine number of images to select from each group
    images_per_group_list, _ = distribute_evenly(target_count, group_count)

    selected_images = []
    offset_index = 0
    for idx, size in enumerate(group_sizes):
        end_idx = offset_index + size
        group = sorted(image_fm[offset_index:end_idx], reverse=True)
        selected_images.extend([img[1] for img in group[:images_per_group_list[idx]]])
        offset_index = end_idx

    print()
    generate_deleted_images_graph(images, selected_images)
    generate_quality_graph(image_fm)

    return selected_images
