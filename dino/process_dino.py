import cv2
import os
import sys

# Import custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from yolo11n.detect import run as yolo_detect  # Use the detection function
from src.extract_roi import extract_roi  # Region of Interest extraction
from dino.color_based.process_color import detect_traffic_light_color  # Traffic light color detection
from ultralytics import YOLO

model = None

def load_model(model_path):
    global model
    if model is None:
        print("Loading YOLO model...")
        model = YOLO(model_path)  # Load the model only once
    return model

def is_square_like(x1, y1, x2, y2, threshold=0.2):
    """
    Determines if a bounding box is close to a square.

    Args:
        x1, y1, x2, y2 (int): Bounding box coordinates.
        threshold (float): Allowed deviation from a perfect square.

    Returns:
        bool: True if the box is square-like, False otherwise.
    """
    width = x2 - x1
    height = y2 - y1
    aspect_ratio = width / height

    # Check if aspect ratio is close to 1 (square)
    return 1 - threshold <= aspect_ratio <= 1 + threshold

def is_object_close(x1, y1, x2, y2, image_height, image_width):
    """
    Determines if an object is close based on its position and size in the image.

    Args:
        x1, y1, x2, y2 (int): Bounding box coordinates.
        image_height (int): Height of the image.
        image_width (int): Width of the image.

    Returns:
        bool: True if the object is close, False otherwise.
    """
    object_width = x2 - x1
    object_height = y2 - y1
    object_area = object_width * object_height
    image_area = image_height * image_width

    object_center_y = (y1 + y2) / 2  # Midpoint of the object

    # If the object takes up more than 10% of the total image area
    is_large = object_area >= 0.1 * image_area  

    # Lower third of the image starts from this y-value
    lower_third_start = image_height * (2 / 3)

    # Check if any part of the object extends into the lower third
    is_near_bottom = y2 >= lower_third_start

    return is_near_bottom and is_large

def process_image(image_path, output_path="output.png"):
    """
    Processes an image to detect **only pedestrian traffic lights** and analyze them.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the processed output image.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image '{image_path}'")
        return

    image_height, image_width, _ = image.shape  # Get image dimensions

    class_names = {
        0: "person",
        1: "bicycle",
        2: "car",
        3: "bus",
        4: "traffic light",
        5: "stop sign",
        6: "chair",
        7: "crosswalks"
    }

    # Step 1: Detect traffic lights with YOLO
    # detect_trafficlight = yolo_detect(model, source=image, classes=[7])  # No class filtering
    detections = yolo_detect(model, source=image)  # No class filtering


    pedestrian_traffic_lights = []
    close_objects = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        
        # Get class name (fallback to "Unknown" if class isn't mapped)
        class_name = class_names.get(cls, f"Unknown ({cls})")

        # Check if the detected object is close
        if is_object_close(x1, y1, x2, y2, image_height, image_width):
            close_objects.append(f"⚠️ a {class_name} is close!")

        if class_name == "traffic light":
            # Only process square-like traffic lights
            if not is_square_like(x1, y1, x2, y2):
                continue

            # Extract region of interest (ROI) for the traffic light
            cropped_light = extract_roi(image, (x1, y1, x2, y2))

            # Process the traffic light color to determine signal
            signal = detect_traffic_light_color(cropped_light)

            # If it's a pedestrian traffic light, save the result
            if signal:
                pedestrian_traffic_lights.append(f"✅ Signal Detected: {signal.upper()}")

    # Output detected pedestrian traffic light signals
    for signal in pedestrian_traffic_lights:
        print(signal)
    
    # Output close object warnings
    for warning in close_objects:
        print(warning)

    # Save the processed image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the output folder exists
    cv2.imwrite(output_path, image)

if __name__ == "__main__":
    model_path = "/Users/patricialee/Development/echovision/runs/detect/train13/weights/best.pt"
    load_model(model_path)  # Load the model once

    process_image(
        "/Users/patricialee/Development/echovision/test_images/intersection-1.png",
        "/Users/patricialee/Development/echovision/output_images/processed.png"
    )
