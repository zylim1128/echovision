import cv2
import os
import sys
import time

# Import custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from yolo11n.detect import run as yolo_detect  # Use the detection function
from src.extract_roi import extract_roi  # Region of Interest extraction
from dino.color_based.process_color import detect_traffic_light_color  # Traffic light color detection
from ultralytics import YOLO

model = None
start_time = time.time()

def load_model(model_path):
    global model
    if model is None:
        print("Loading YOLO model...")
        # model = YOLO(model_path).to("cuda")
        model = YOLO(model_path)
        print(f"YOLO is running on: {'GPU' if next(model.model.parameters()).is_cuda else 'CPU'}")
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

    # Step 1: Detect traffic lights with YOLO
    detections = yolo_detect(model, source=image_path, classes=[4])  # 4 is the traffic light class now (updated)

    pedestrian_traffic_lights = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det

        # Only process square-like traffic lights
        if not is_square_like(x1, y1, x2, y2):
            continue

        # Extract region of interest (ROI) for the traffic light
        # test run time for extract_roi
        start = time.time()
        cropped_light = extract_roi(image, (x1, y1, x2, y2))
        print(f"ROI Extraction Time: {time.time() - start:.4f} sec")

        # Process the traffic light color to determine signal
        start = time.time()
        signal = detect_traffic_light_color(cropped_light)
        print(f"Color Processing Time: {time.time() - start:.4f} sec")

        # If it's a pedestrian traffic light, save the result
        if signal:
            pedestrian_traffic_lights.append(f"✅ Signal Detected: {signal.upper()}")

    # Output detected pedestrian traffic light signals
    for signal in pedestrian_traffic_lights:
        print(signal)

    print(f"Total Processing Time: {time.time() - start_time:.4f} sec")

    # Save the processed image
    # Comment out below to increase runtime
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the output folder exists
    # cv2.imwrite(output_path, image)

if __name__ == "__main__":
    print("When do we get here?")
    model_path = "/mmfs1/gscratch/krishna/zylim/echovision/runs/detect/train17/weights/best.pt"
    load_model(model_path)  # Load the model once

    process_image(
        "/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png",
        "/mmfs1/gscratch/krishna/zylim/echovision/output_images/processed1.png"
    )