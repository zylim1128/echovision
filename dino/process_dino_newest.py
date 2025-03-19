import cv2
import os
import sys

# Add parent directory to sys.path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from yolo11n.detect import run as yolo_detect
from src.extract_roi import extract_roi
from dino.color_based.process_color import detect_traffic_light_color, TrafficSignalError
from ultralytics import YOLO

TRAFFIC_LIGHT_YOLO_IDX = 4
model = None

def _load_model(model_path):
    global model
    if model is None:
        print("Loading YOLO model...")
        model = YOLO(model_path)
    return model

def _is_square_like(x1, y1, x2, y2, threshold=0.15):
    width = x2 - x1
    height = y2 - y1
    aspect_ratio = width / height
    return 1 - threshold <= aspect_ratio <= 1 + threshold

def _is_box_shape(x1, y1, x2, y2, threshold=0.2):
    width = x2 - x1
    height = y2 - y1
    return abs(width - height) / max(width, height) < threshold

def estimate_distance(x1, y1, x2, y2, image_height, image_width):
    object_height = y2 - y1
    object_width = x2 - x1
    object_area_ratio = (object_width * object_height) / (image_width * image_height)

    if object_area_ratio > 0.15:
        return "very close"
    elif object_area_ratio > 0.07:
        return "close"
    elif object_area_ratio > 0.03:
        return "a few meters away"
    else:
        return "far"

def get_clock_position(x1, y1, x2, y2, image_width, image_height):
    center_x = image_width / 2
    object_x = (x1 + x2) / 2

    if object_x < center_x * 0.8:
        return "to your left"
    elif object_x > center_x * 1.2:
        return "to your right"
    else:
        return "ahead"

def process_image(image_path, model):
    image = cv2.imread(image_path)
    if image is None:
        return f"Error: Could not load image '{image_path}'"

    image_height, image_width, _ = image.shape
    detections = yolo_detect(model, source=image, classes=[TRAFFIC_LIGHT_YOLO_IDX])
    pedestrian_traffic_lights = []
    warnings = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det

        if not _is_square_like(x1, y1, x2, y2) or not _is_box_shape(x1, y1, x2, y2):
            continue

        cropped_light = extract_roi(image, (x1, y1, x2, y2))
        distance = estimate_distance(x1, y1, x2, y2, image_height, image_width)
        position = get_clock_position(x1, y1, x2, y2, image_width, image_height)

        try:
            signal = detect_traffic_light_color(cropped_light)
            msg = f"✅ Signal Detected: {signal.upper()} {position}, {distance}."
            pedestrian_traffic_lights.append(msg)
            if distance in ["very close", "close"]:
                warnings.append(f"⚠️ Warning: pedestrian light {position}, {distance}!")
        except (IOError, TrafficSignalError, Exception) as e:
            return f"Error processing {image_path}: {e}"

    return "\n".join(pedestrian_traffic_lights + warnings) if pedestrian_traffic_lights else "No traffic lights detected."

def process_folder(input_folder, output_file, model_path):
    model = _load_model(model_path)
    results = []

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.join(input_folder, file_name)
            result = process_image(image_path, model)
            results.append(f"{file_name}:\n{result}\n")
            print(f"Processed {file_name}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines("\n".join(results))

    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    input_folder = "../final-image-walk/walk" # folder of images
    output_file = "../final-output-walk/walk_output_2.txt" # store txt result
    model_path = "../runs/detect/train17/weights/best.pt"
    process_folder(input_folder, output_file, model_path)
