import os

# Base dataset directory
DATASET_DIR = "/mmfs1/gscratch/krishna/zylim/echovision/yolo11n/datasets/coco"

# Define subdirectories
SPLITS = ["train", "val", "test"]

# Classes to remove
UNWANTED_CLASSES = {4, 8, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 
                    27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 
                    44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 57, 58, 59, 68, 69, 
                    70, 71, 72, 75, 76, 77, 78, 79}

def clean_labels_and_images(dataset_dir):
    for split in SPLITS:
        labels_dir = os.path.join(dataset_dir, split, "labels")
        images_dir = os.path.join(dataset_dir, split, "images")

        if not os.path.exists(labels_dir):
            print(f"Skipping {split}, labels directory not found.")
            continue

        for filename in os.listdir(labels_dir):
            if filename.endswith(".txt"):  # Only process label files
                label_path = os.path.join(labels_dir, filename)
                image_path_jpg = os.path.join(images_dir, filename.replace(".txt", ".jpg"))
                image_path_png = os.path.join(images_dir, filename.replace(".txt", ".png"))

                with open(label_path, "r") as f:
                    lines = f.readlines()

                # Remove lines containing unwanted class IDs
                filtered_lines = [line for line in lines if int(line.split()[0]) not in UNWANTED_CLASSES]

                if filtered_lines:
                    # Overwrite label file only if changes were made
                    if len(filtered_lines) < len(lines):
                        with open(label_path, "w") as f:
                            f.writelines(filtered_lines)
                        print(f"Updated {split}/{filename}, removed {len(lines) - len(filtered_lines)} labels.")
                else:
                    # Delete empty label file
                    os.remove(label_path)
                    print(f"Deleted empty label file: {split}/{filename}")

                    # Delete corresponding image if it exists
                    for image_path in [image_path_jpg, image_path_png]:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            print(f"Deleted corresponding image: {split}/{os.path.basename(image_path)}")

# Run the cleaning process
clean_labels_and_images(DATASET_DIR)
