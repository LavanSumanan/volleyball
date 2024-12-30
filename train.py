from ultralytics import YOLO

model = YOLO("models/yolo11n.pt")  # pass any model type
results = model.train(epochs=5)
