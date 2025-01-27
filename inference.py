# for testing
from ultralytics import YOLO
import cv2

# Load trained model
model = YOLO("")  # TODO: add path to trained model

# Run inference on an image
image_path = "test.jpg"
results = model(image_path)
results.show()