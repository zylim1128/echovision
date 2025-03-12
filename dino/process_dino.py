# import cv2
# import os
# import sys
# import time
# import math

# # Import custom modules
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from yolo11n.detect import run as yolo_detect  # Use the detection function
# from src.extract_roi import extract_roi  # Region of Interest extraction
# from dino.color_based.process_color import detect_traffic_light_color  # Traffic light color detection
# from ultralytics import YOLO

# model = None
# start_time = time.time()

# def load_model(model_path):
#     global model
#     if model is None:
#         print("Loading YOLO model...")
#         model = YOLO(model_path)
#         print(f"YOLO is running on: {'GPU' if next(model.model.parameters()).is_cuda else 'CPU'}")
#     return model

# def is_square_like(x1, y1, x2, y2, threshold=0.2):
#     width = x2 - x1
#     height = y2 - y1
#     aspect_ratio = width / height
#     return 1 - threshold <= aspect_ratio <= 1 + threshold

# def is_object_close(x1, y1, x2, y2, image_height, image_width):
#     object_width = x2 - x1
#     object_height = y2 - y1
#     object_area = object_width * object_height
#     image_area = image_height * image_width

#     is_large = object_area >= 0.1 * image_area  
#     lower_third_start = image_height * (2 / 3)

#     is_near_bottom = y2 >= lower_third_start
#     return is_near_bottom and is_large

# def get_clock_position(x1, y1, x2, y2, image_width, image_height):
#     center_x = image_width / 2
#     center_y = image_height / 2
#     object_x = (x1 + x2) / 2
#     object_y = (y1 + y2) / 2

#     angle_radians = math.atan2(center_y - object_y, object_x - center_x)
#     angle_degrees = math.degrees(angle_radians)
#     angle_degrees = max(-90, min(angle_degrees, 90))  

#     clock_positions = {
#         -60: "slightly to your left", -30: "in front of you", 
#         0: "right in front of you", 30: "in front of you", 60: "slightly to your right"
#     }
    
#     nearest_30 = round(angle_degrees / 30) * 30  
#     return clock_positions.get(nearest_30, "12 o'clock")  

# def process_image(image_path, output_path="output.png"):
#     image = cv2.imread(image_path)
#     if image is None:
#         print(f"Error: Could not load image '{image_path}'")
#         return

#     image_height, image_width, _ = image.shape  
#     class_names = {4: "traffic light"}

#     detections = yolo_detect(model, source=image_path, classes=[4])  
#     pedestrian_traffic_lights = []
#     close_objects = []

#     for det in detections:
#         x1, y1, x2, y2, conf, cls = det
#         class_name = class_names.get(cls, f"Unknown ({cls})")

#         if is_object_close(x1, y1, x2, y2, image_height, image_width):
#             clock_position = get_clock_position(x1, y1, x2, y2, image_width, image_height)
#             close_objects.append(f"Warning: {class_name} {clock_position} is close!")
#             cv2.putText(image, f"⚠ {class_name} close!", (int(x1), int(y1) - 15),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

#         if class_name == "traffic light" and is_square_like(x1, y1, x2, y2):
#             start = time.time()
#             cropped_light = extract_roi(image, (x1, y1, x2, y2))
#             print(f"ROI Extraction Time: {time.time() - start:.4f} sec")

#             start = time.time()
#             signal = detect_traffic_light_color(cropped_light)
#             print(f"Color Processing Time: {time.time() - start:.4f} sec")

#             if signal:
#                 pedestrian_traffic_lights.append(f"✅ Signal Detected: {signal.upper()}")
#                 cv2.putText(image, f"{signal.upper()}", (int(x1), int(y2) + 20),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

#         cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
#         label = f"{class_name} ({conf:.2f})"
#         cv2.putText(image, label, (int(x1), int(y1) - 5),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

#     for signal in pedestrian_traffic_lights:
#         print(signal)
    
#     for warning in close_objects:
#         print(warning)

#     print(f"Total Processing Time: {time.time() - start_time:.4f} sec")

#     os.makedirs(os.path.dirname(output_path), exist_ok=True)  
#     cv2.imwrite(output_path, image)
#     print(f"Processed image saved at {output_path}")

# if __name__ == "__main__":
#     model_path = "/mmfs1/gscratch/krishna/zylim/echovision/runs/detect/train17/weights/best.pt"
#     load_model(model_path)

#     process_image(
#         "/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png",
#         "/mmfs1/gscratch/krishna/zylim/echovision/output_images/processed1.png"
#     )

import cv2
import os
import sys
import time
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from yolo11n.detect import run as yolo_detect  
from src.extract_roi import extract_roi  
from dino.color_based.process_color import detect_traffic_light_color  
from ultralytics import YOLO

model = None
start_time = time.time()

def load_model(model_path):
    global model
    if model is None:
        print("Loading YOLO model...")
        model = YOLO(model_path)
        print(f"YOLO is running on: {'GPU' if next(model.model.parameters()).is_cuda else 'CPU'}")
    return model

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

def process_image(image_path, output_path="output.png"):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image '{image_path}'", flush=True)
        return

    image_height, image_width, _ = image.shape  
    class_names = {4: "traffic light"}

    detections = yolo_detect(model, source=image_path, classes=[4])  
    pedestrian_traffic_lights = []
    close_objects = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det
        class_name = class_names.get(cls, f"Unknown ({cls})")
        distance_estimate = estimate_distance(x1, y1, x2, y2, image_height, image_width)
        clock_position = get_clock_position(x1, y1, x2, y2, image_width, image_height)

        if class_name == "traffic light" and (x2 - x1) / (y2 - y1) >= 0.8:
            cropped_light = extract_roi(image, (x1, y1, x2, y2))
            signal = detect_traffic_light_color(cropped_light)

            if signal:
                pedestrian_traffic_lights.append(f"✅ Signal Detected: {signal.upper()} {clock_position}, {distance_estimate}.")
        
        if distance_estimate in ["very close", "close"]:
            close_objects.append(f"Warning: {class_name} {clock_position}, {distance_estimate}!")
        
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (255, 255, 0), 2)
        cv2.putText(image, f"{class_name} ({conf:.2f})", (int(x1), int(y1) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    for message in pedestrian_traffic_lights + close_objects:
        print(message, flush=True)  # Force output immediately for piping

    print(f"Total Processing Time: {time.time() - start_time:.4f} sec", flush=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)  
    cv2.imwrite(output_path, image)
    print(f"Processed image saved at {output_path}", flush=True)

if __name__ == "__main__":
    model_path = "/mmfs1/gscratch/krishna/zylim/echovision/runs/detect/train17/weights/best.pt"
    load_model(model_path)

    process_image(
        "/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png",
        "/mmfs1/gscratch/krishna/zylim/echovision/output_images/processed1.png"
    )
