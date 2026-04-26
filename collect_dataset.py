import cv2
import os

folder = "asl_dataset"

classes = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ") 

cap = cv2.VideoCapture(0)

current = 0
count = 0
max_images = 30

while True:

    name = classes[current]

    path = os.path.join(folder, name)

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    cv2.putText(
        frame,
        f"Class: {name}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        f"Images: {count}/{max_images}",
        (20,80),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,0),
        2
    )

    cv2.putText(
        frame,
        "SPACE=Capture | ENTER=Next | ESC=Exit",
        (20,120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255,255,255),
        2
    )

    cv2.imshow("Dataset Collector", frame)

    key = cv2.waitKey(1)

    # SPACE
    if key == 32 and count < max_images:

        filename = os.path.join(path, f"{count}.jpg")

        cv2.imwrite(filename, frame)

        count += 1

    # ENTER
    if key == 13:

        current += 1
        count = 0

        if current >= len(classes):
            break

    # ESC
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()