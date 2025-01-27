from ultralytics import YOLO

# Load a model (ensure the model path is correct)
model = YOLO("yolo11n.pt")  # Use "yolov8n.pt" instead of "yolo11n.pt" (typo fix)

# Train the model (optional, if training on a custom dataset)
train_results = model.train(
    data="dataset.yaml",  # Path to dataset YAML
    epochs=50,  # Number of training epochs
    imgsz=640,  # Training image size
    device="cpu",  # Change to 'cuda' if using GPU
)


