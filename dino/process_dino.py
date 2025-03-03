import cv2
import torch
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from yolo11n.detect import run as yolo_detect
from src.extract_roi import extract_roi
from dino.color_based.process_color import detect_traffic_light_color

def process_image(image_path):
    """
    Processes a single image to detect traffic lights and analyze them.

    Args:
        image_path (str): Path to the input image.
    """
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image '{image_path}'")
        return

    # Step 1: Detect traffic lights with YOLO
    detections = yolo_detect(source=image, classes=[9])  # Assuming class 9 is 'traffic light'

    for det in detections:
        x1, y1, x2, y2, conf, cls = det

        # Step 2: Extract the detected region
        cropped_light = extract_roi(image, (x1, y1, x2, y2))

        # Step 3: Process the traffic light color
        signal = detect_traffic_light_color(cropped_light)

        # Step 4: Draw detection results on the image
        label = f"{signal.upper()} ({conf:.2f})"
        color = (0, 255, 0) if signal == "walk" else (0, 0, 255)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Show the processed image
    cv2.imshow("Processed Image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process_image("/mmfs1/gscratch/krishna/zylim/echovision/test_images/intersection-1.png")  # Change to your test image path




# For video
# import cv2
# import torch
# from yolo11n.detect import run as yolo_detect
# from src.extract_roi import extract_roi
# from dino.color_based.process_color import detect_traffic_light_color

# def process_video(video_path=None):
#     """
#     Processes a video feed to detect traffic lights using YOLO and analyze them with process_color.py.

#     Args:
#         video_path (str or None): Path to a video file. If None, uses webcam.
#     """
#     # Open video source (file or webcam)
#     cap = cv2.VideoCapture(0 if video_path is None else video_path)

#     if not cap.isOpened():
#         print("Error: Could not open video source.")
#         return

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break  # Exit loop if video ends

#         # Step 1: Use YOLO to detect traffic lights
#         detections = yolo_detect(source=frame, classes=[9])  # Assuming class 9 is 'traffic light'

#         for det in detections:
#             x1, y1, x2, y2, conf, cls = det
#             cropped_light = extract_roi(frame, (x1, y1, x2, y2))

#             # Step 2: Process the detected traffic light using color analysis
#             signal = detect_traffic_light_color(cropped_light)

#             # Step 3: Draw detection on the frame
#             label = f"{signal.upper()} ({conf:.2f})"
#             color = (0, 255, 0) if signal == "walk" else (0, 0, 255)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

#         # Show processed video
#         cv2.imshow("Traffic Light Detection", frame)
#         if cv2.waitKey(1) & 0xFF == ord("q"):
#             break  # Press 'q' to quit

#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     process_video("test_video.mp4")  # Change this to None for webcam
