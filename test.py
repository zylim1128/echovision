from ultralytics import YOLO
import cv2

# Load your trained model
model = YOLO("runs/detect/train6/weights/best.pt")
# print(model.names)

# Test on a single image
# results = model("abbey_road.jpg", conf=0.2)
results = model("testing.jpg", conf=0.25)
results[0].save("output.jpg")

# Show the result
results[0].show()