import os
import random
import shutil
import json
from pycocotools.coco import COCO

# Update this to point to your COCO dataset
coco_path = "./yolo11n/datasets/coco"
annotation_file = os.path.join(coco_path, "annotations/instances_train2017.json")
image_dir = os.path.join(coco_path, "images/train2017")

# YOLO output structure
output_dirs = {
    "train": {"images": os.path.join(coco_path, "train/images"), "labels": os.path.join(coco_path, "train/labels")},
    "val": {"images": os.path.join(coco_path, "val/images"), "labels": os.path.join(coco_path, "val/labels")},
    "test": {"images": os.path.join(coco_path, "test/images"), "labels": os.path.join(coco_path, "test/labels")}
}

# Create directories if they don’t exist
for split in output_dirs.values():
    os.makedirs(split["images"], exist_ok=True)
    os.makedirs(split["labels"], exist_ok=True)

# Load COCO dataset
coco = COCO(annotation_file)
categories = coco.loadCats(coco.getCatIds())
category_map = {cat["id"]: cat["name"] for cat in categories}

# Store selected images per class
selected_images = {}

# Step 1: Select 150 images per class
for cat_id in category_map.keys():
    img_ids = coco.getImgIds(catIds=[cat_id])
    random.shuffle(img_ids)  # Shuffle to randomize selection
    selected_images[cat_id] = img_ids[:150]  # Select 150 images per class

# Step 2: Distribute images into train (100), test (30), val (20)
split_ratios = {"train": 100, "test": 30, "val": 20}
image_splits = {"train": [], "test": [], "val": []}

for cat_id, img_list in selected_images.items():
    image_splits["train"].extend(img_list[:100])
    image_splits["test"].extend(img_list[100:130])
    image_splits["val"].extend(img_list[130:150])

# Ensure unique image selection
for key in image_splits:
    image_splits[key] = list(set(image_splits[key]))

# Step 3: Copy images & labels to respective directories
for split, img_ids in image_splits.items():
    for img_id in img_ids:
        img_info = coco.loadImgs(img_id)[0]
        img_filename = img_info["file_name"]
        src_img_path = os.path.join(image_dir, img_filename)
        dst_img_path = os.path.join(output_dirs[split]["images"], img_filename)

        # Copy image
        if os.path.exists(src_img_path):
            shutil.copy(src_img_path, dst_img_path)

        # Convert and copy labels
        ann_ids = coco.getAnnIds(imgIds=[img_id])
        annotations = coco.loadAnns(ann_ids)

        label_file = os.path.splitext(img_filename)[0] + ".txt"
        label_path = os.path.join(output_dirs[split]["labels"], label_file)

        with open(label_path, "w") as f:
            for ann in annotations:
                cat_id = ann["category_id"]
                coco_class_index = list(category_map.keys()).index(cat_id)  # Convert to YOLO format (0-indexed)
                bbox = ann["bbox"]
                x, y, w, h = bbox

                # Normalize values (x_center, y_center, w, h) for YOLO
                x_center = (x + w / 2) / img_info["width"]
                y_center = (y + h / 2) / img_info["height"]
                w = w / img_info["width"]
                h = h / img_info["height"]

                f.write(f"{coco_class_index} {x_center} {y_center} {w} {h}\n")

print("✅ COCO dataset successfully sampled and converted to YOLO format!")
