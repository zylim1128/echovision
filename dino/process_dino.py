# import cv2
# import os
# import sys
# import time

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from yolo11n.detect import run as yolo_detect
# from src.extract_roi import extract_roi
# from dino.color_based.process_color import detect_traffic_light_color

# def is_square_like(x1, y1, x2, y2, threshold=0.2):
#     width = x2 - x1
#     height = y2 - y1
#     aspect_ratio = width / height
#     return 1 - threshold <= aspect_ratio <= 1 + threshold

# def process_video(video_path=None, output_path=None):
#     """
#     Processes a video stream to detect pedestrian traffic lights.
    
#     Args:
#         video_path (str or None): Path to the video file. If None, uses webcam.
#         output_path (str or None): Path to save the processed video. If None, video is not saved.
#     """
#     cap = cv2.VideoCapture(0 if video_path is None else video_path)

#     if not cap.isOpened():
#         print("Error: Could not open video source.")
#         return

#     # Get video properties (only needed if saving output)
#     width  = int(cap.get(3))
#     height = int(cap.get(4))
#     fps    = cap.get(cv2.CAP_PROP_FPS)

#     # Define video writer if output is needed
#     out = None
#     if output_path:
#         fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 files
#         out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break  # Exit loop if the video ends

#         start_time = time.time()  # For FPS calculation

#         # Step 1: Detect traffic lights with YOLO
#         detections = yolo_detect(source=frame, classes=[9])  # 9 is traffic light class

#         for det in detections:
#             x1, y1, x2, y2, conf, cls = det

#             if not is_square_like(x1, y1, x2, y2):
#                 continue  # Skip non-square traffic lights

#             # Step 2: Extract detected region
#             cropped_light = extract_roi(frame, (x1, y1, x2, y2))

#             # Step 3: Process the traffic light color
#             signal = detect_traffic_light_color(cropped_light)

#             # Step 4: Draw detection results on the frame
#             label = f"{signal.upper()} ({conf:.2f})"
#             color = (0, 255, 0) if signal == "walk" else (0, 0, 255)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#         # Show the processed frame
#         cv2.imshow("Traffic Light Detection", frame)

#         # Save the frame if output video is enabled
#         if out:
#             out.write(frame)

#         # Calculate FPS
#         elapsed_time = time.time() - start_time
#         print(f"Frame Time: {elapsed_time:.3f}s, FPS: {1/elapsed_time:.2f}")

#         # Exit on 'q' key press
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break

#     cap.release()
#     if out:
#         out.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     process_video(
#         video_path="/mmfs1/gscratch/krishna/zylim/echovision/test_videos/intersection.mp4",
#         output_path="/mmfs1/gscratch/krishna/zylim/echovision/output_videos/processed.mp4"
#     )


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
    detections = yolo_detect(model, source=image, classes=[7])  # 7 is the traffic light class now (updated)

    pedestrian_traffic_lights = []

    for det in detections:
        x1, y1, x2, y2, conf, cls = det

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

    # Save the processed image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure the output folder exists
    cv2.imwrite(output_path, image)

if __name__ == "__main__":
    model_path = "/mmfs1/gscratch/krishna/zylim/echovision/runs/detect/train15/weights/best.pt"
    load_model(model_path)  # Load the model once

    process_image(
        "/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png",
        "/mmfs1/gscratch/krishna/zylim/echovision/output_images/processed.png"
    )