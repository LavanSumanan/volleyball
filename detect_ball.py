import cv2
from ultralytics import YOLO

yolo = YOLO("models/best.pt")

video_path = "./vids/fullgame.mov"
cap = cv2.VideoCapture(video_path)
# Calculate the new position
new_frame = 5000
# Set the new position
cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = yolo.track(frame, stream=True)

    for result in results:
        boxes = result.boxes.cpu().numpy()
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].astype(int)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow("YOLO Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
