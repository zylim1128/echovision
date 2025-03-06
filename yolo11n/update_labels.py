import os
import glob

# Path to your dataset
dataset_path = "/mmfs1/gscratch/krishna/zylim/echovision/yolo11n/datasets/crosswalk"

# Folders to process
subsets = ["train", "val", "test"]

def update_labels(folder):
    label_files = glob.glob(os.path.join(folder, "labels", "*.txt"))
    
    for file in label_files:
        with open(file, "r") as f:
            lines = f.readlines()

        # Modify labels
        updated_lines = []
        for line in lines:
            parts = line.strip().split()
            if parts and parts[0] == "80":  # Change label 0 to 80
                parts[0] = "21"  # now update to 21 for reindexing
            updated_lines.append(" ".join(parts))

        # Save changes
        with open(file, "w") as f:
            f.write("\n".join(updated_lines) + "\n")

for subset in subsets:
    update_labels(os.path.join(dataset_path, subset))

print("Labels updated successfully!")
