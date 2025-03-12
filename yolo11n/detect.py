import cv2
import torch
from ultralytics import YOLO

# Path to your fine-tuned YOLO model
# model_path = "/mmfs1/gscratch/krishna/zylim/echovision/runs/detect/train13/weights/best.pt"
# model = YOLO(model_path)

def run(model, source, classes=None):
    """
    Run YOLO object detection on an image or frame.

    Args:
        source (numpy array or str): Image path or frame array.
        classes (list, optional): List of class IDs to filter (e.g., [9] for traffic lights).

    Returns:
        list: Detected bounding boxes [(x1, y1, x2, y2, confidence, class_id), ...]
    """
    # Run detection
    results = model(source)[0]

    detections = []
    for r in results.boxes.data.cpu().numpy():  # Iterate through detections
        x1, y1, x2, y2, conf, cls = r
        if classes is None or int(cls) in classes:  # Filter based on classes (traffic lights)
            detections.append((int(x1), int(y1), int(x2), int(y2), float(conf), int(cls)))
    
    return detections