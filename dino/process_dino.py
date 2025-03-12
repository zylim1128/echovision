import cv2
import os
import sys

# Import custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from yolo11n.detect import run as yolo_detect  # Use the detection function
from src.extract_roi import extract_roi  # Region of Interest extraction
from dino.color_based.process_color import detect_traffic_light_color, TrafficSignalError  # Traffic light color detection
from ultralytics import YOLO

TRAFFIC_LIGHT_YOLO_IDX = 4

model = None

def _load_model(model_path):
    global model
    if model is None:
        print("Loading YOLO model...")
        model = YOLO(model_path)  # Load the model only once
    return model

def _is_square_like(x1, y1, x2, y2, threshold=0.2):
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

def process_image(image_path, model, output_path="output.png"):
    """
    Processes an image to detect **only pedestrian traffic lights** and analyze them.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the processed output image.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        stderr(f"Error: Could not load image '{image_path}'")
        return

    # Step 1: Detect traffic lights with YOLO
    detections = yolo_detect(model, source=image, classes=[TRAFFIC_LIGHT_YOLO_IDX])  # 7 is the traffic light class now (updated)
    # print(f"detections = {detections}")
    pedestrian_traffic_lights = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det

        # Only process square-like traffic lights
        if not _is_square_like(x1, y1, x2, y2):
            continue

        # Extract region of interest (ROI) for the traffic light
        cropped_light = extract_roi(image, (x1, y1, x2, y2))

        try:
            # Process the traffic light color to determine signal
            signal = detect_traffic_light_color(cropped_light)

            ## TODO: store results with the bbox
            # If it's a pedestrian traffic light, save the result
            pedestrian_traffic_lights.append(f"✅ Signal Detected: {signal.upper()}")
        except IOError as e:
            stderr(f"IOError: {e}")
            
        except TrafficSignalError as e:
            stderr(f"TrafficSignalError: {e}")
            
        except Exception as e:
            stderr(f"Unexpected error: {e}")


    # Output detected pedestrian traffic light signals
    for signal in pedestrian_traffic_lights:
        print(signal)
    # return '\n'.join(pedestrian_traffic_lights)  ## TODO

    # optional parameter to store annotated image
    # Save the processed image
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the output folder exists
    # cv2.imwrite(output_path, image)

if __name__ == "__main__":
    model_path = "runs/detect/train17/weights/best.pt"
    model = _load_model(model_path)  # Load the model once

    process_image(    \
        # "/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png",
        # "/mmfs1/gscratch/krishna/zylim/echovision/output_images/processed.png",
        "test_images/intersection-9.png",  \
        model
    )
