import os
import cv2
import argparse
from process_color import detect_traffic_light_color

def test_images_in_folder(folder_path):
    """
    Tests all images in the specified folder using process_color.py.

    Args:
        folder_path (str): Path to the folder containing test images.
    """
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' not found.")
        return
    
    # Get all image files in the folder
    image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.jpeg'))]

    if not image_files:
        print(f"No image files found in '{folder_path}'")
        return

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        result = detect_traffic_light_color(image_path)
        print(f"{image_file}: Detected signal -> {result}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test process_color.py on sample images.")
    parser.add_argument("--folder", type=str, default="test_images", 
                        help="Folder containing test images.")
    args = parser.parse_args()

    # Run the test on the given folder
    test_images_in_folder(args.folder)
