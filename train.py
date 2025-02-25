from ultralytics import YOLO

# can run this command: yolo train model=yolo11n.pt data=yolo11n/datasets/merged_data.yaml epochs=50 imgsz=640

# Load a model
model = YOLO("yolo11n.pt")

# Train the model
train_results = model.train(
    data="yolo11n/datasets/merged_data.yaml",  # path to dataset YAML
    epochs=100,  # number of training epochs
    imgsz=640,  # training image size
    device="cpu",  # device to run on, i.e. device=0 or device=0,1,2,3 or device=cpu
)

# Evaluate model performance on the validation set
metrics = model.val()