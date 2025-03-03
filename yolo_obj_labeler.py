import os
import argparse

def generate_yolo_label(image_width, image_height, top_left, bottom_right):
    """
    Generates YOLO label from top-left and bottom-right coordinates.

    Parameters:
    - image_width (int): Width of the image.
    - image_height (int): Height of the image.
    - top_left (tuple): (x1, y1) - Top-left coordinate of the bounding box.
    - bottom_right (tuple): (x2, y2) - Bottom-right coordinate of the bounding box.
    # - class_id (int): Class ID of the object (integer).
    # - output_dir (str): Directory to save the YOLO label file.
    """
    # Extract the coordinates
    x1, y1 = top_left
    x2, y2 = bottom_right

    # Calculate width and height of the bounding box
    bbox_width = x2 - x1
    bbox_height = y2 - y1

    # Calculate the center of the bounding box
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2

    # Normalize the coordinates by the image dimensions
    x_center_norm = round(x_center / image_width, 7)
    y_center_norm = round(y_center / image_height, 7)
    bbox_width_norm = round(bbox_width / image_width, 7)
    bbox_height_norm = round(bbox_height / image_height, 7)

    # Prepare the YOLO label format: class_id x_center y_center width height
    label = f"{x_center_norm} {y_center_norm} {bbox_width_norm} {bbox_height_norm}\n"

    # Create output directory if it doesn't exist
    print(label)
    # os.makedirs(output_dir, exist_ok=True)

    # Save label to file with the same name as the image, but with .txt extension
    # label_filename = os.path.join(output_dir, "image_label.txt")  # You can change the filename convention
    # with open(label_filename, "w") as f:
    #     f.write(label)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate YOLO label from bounding box coordinates")
    
    # Define the arguments
    parser.add_argument("image_width", type=int, help="Width of the image")
    parser.add_argument("image_height", type=int, help="Height of the image")
    parser.add_argument("top_left", type=int, nargs=2, help="Top-left coordinate (x1, y1) of the bounding box")
    parser.add_argument("bottom_right", type=int, nargs=2, help="Bottom-right coordinate (x2, y2) of the bounding box")
    # parser.add_argument("class_id", type=int, help="Class ID of the object")
    # parser.add_argument("output_dir", type=str, help="Directory to save the YOLO label file")

    return parser.parse_args()

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()

    # Generate the YOLO label
    generate_yolo_label(args.image_width, args.image_height, tuple(args.top_left), tuple(args.bottom_right))
