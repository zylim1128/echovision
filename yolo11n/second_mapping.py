import os

# Second remapping: Reduce to only 8 classes
second_remapping = {
    0: 0,  # person
    1: 1,  # bicycle
    2: 2,  # car
    4: 3,  # bus
    7: 4,  # traffic light
    9: 5,  # stop sign
    10: 6, # chair
    21: 7  # crosswalk
}

dataset_root = "/mmfs1/gscratch/krishna/zylim/echovision/yolo11n/datasets/training_images"
subfolders = ["train", "val", "test"]

for subfolder in subfolders:
    labels_dir = os.path.join(dataset_root, subfolder, "labels")
    images_dir = os.path.join(dataset_root, subfolder, "images")  # Assuming images are here

    if not os.path.exists(labels_dir):
        print(f"Skipping {subfolder}, no labels folder found.")
        continue

    # Iterate through all label files in the current subfolder
    for label_file in os.listdir(labels_dir):
        if label_file.endswith(".txt"):  # Assuming label files are text files
            label_path = os.path.join(labels_dir, label_file)

            # Open and read the label file
            with open(label_path, "r") as f:
                lines = f.readlines()

            # List to hold the updated lines
            new_lines = []

            # Iterate through each line in the label file
            for line in lines:
                parts = line.strip().split()  # Split into class index and other parts
                old_class_index = int(parts[0])

                # Apply the second remapping ONLY if the class is in the list
                if old_class_index in second_remapping:
                    new_class_index = second_remapping[old_class_index]
                    new_line = f"{new_class_index} " + " ".join(parts[1:])
                    new_lines.append(new_line)

            # Overwrite the file ONLY if there are valid labels left
            if new_lines:
                with open(label_path, "w") as f:
                    f.write("\n".join(new_lines) + "\n")
                print(f"Updated labels in {subfolder}/{label_file}")
            else:
                # If all labels were removed, delete the label file
                os.remove(label_path)
                print(f"Deleted {subfolder}/{label_file} (no valid labels left)")

                # Find and delete the corresponding image file
                base_name = os.path.splitext(label_file)[0]
                for ext in [".jpg", ".jpeg", ".png"]:  # Add more extensions if needed
                    image_path = os.path.join(images_dir, base_name + ext)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        print(f"Deleted corresponding image: {subfolder}/images/{base_name + ext}")
                        break  # Stop after deleting one image

print("Second remapping applied successfully across all subfolders!")
