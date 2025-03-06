import os

# Define the class remapping: map old class index to new class index
class_remapping = {
    0: 0,   # person -> person
    1: 1,   # bicycle -> bicycle
    2: 2,   # car -> car
    3: 3,   # motorcycle -> motorcycle
    5: 4,   # bus -> bus
    6: 5,   # train -> train
    7: 6,   # truck -> truck
    9: 7,   # traffic light -> traffic light
    10: 8,  # fire hydrant -> fire hydrant
    11: 9,  # stop sign -> stop sign
    56: 10, # chair -> chair
    60: 11, # dining table -> dining table
    61: 12, # toilet -> toilet
    62: 13, # tv -> tv
    63: 14, # laptop -> laptop
    64: 15, # mouse -> mouse
    65: 16, # remote -> remote
    66: 17, # keyboard -> keyboard
    67: 18, # cell phone -> cell phone
    73: 19, # book -> book
    74: 20, # clock -> clock
    80: 21  # crosswalks -> crosswalks
}

# Define the root directory of your dataset
dataset_root = "/mmfs1/gscratch/krishna/zylim/echovision/yolo11n/datasets/coco"

# Subfolders to process
subfolders = ["train", "val", "test"]

# Iterate through each subfolder
for subfolder in subfolders:
    label_dir = os.path.join(dataset_root, subfolder, "labels")

    # Ensure the labels directory exists
    if not os.path.exists(label_dir):
        print(f"Skipping {subfolder}, no labels folder found.")
        continue

    # Iterate through all label files in the current subfolder's 'labels' directory
    for label_file in os.listdir(label_dir):
        if label_file.endswith(".txt"):  # Assuming label files are text files
            label_path = os.path.join(label_dir, label_file)

            # Open and read the label file
            with open(label_path, "r") as f:
                lines = f.readlines()

            # List to hold the updated lines
            new_lines = []

            # Iterate through each line in the label file
            for line in lines:
                parts = line.strip().split()  # Split into class index and other parts
                old_class_index = int(parts[0])

                # If the class index needs to be remapped, update it
                if old_class_index in class_remapping:
                    new_class_index = class_remapping[old_class_index]
                    # Reconstruct the line with the updated class index
                    new_line = f"{new_class_index} " + " ".join(parts[1:])
                    new_lines.append(new_line)
                else:
                    # If no remapping is needed, keep the original line
                    new_lines.append(line.strip())

            # Write the updated labels back to the file
            with open(label_path, "w") as f:
                f.write("\n".join(new_lines) + "\n")

            print(f"Updated labels in {label_file}")

print("All label files updated successfully!")
